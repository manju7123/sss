const express = require('express');
const { open } = require('sqlite');
const sqlite3 = require('sqlite3');
const path = require('path');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const fetch = require('node-fetch');
require('dotenv').config();

const databasePath = path.join(__dirname, 'database.db');
const app = express();
app.use(express.json());

let database = null;

const initializeDbAndServer = async () => {
  try {
    database = await open({
      filename: databasePath,
      driver: sqlite3.Database,
    });

    // Create tables if they don't exist
    await createTables();

    app.listen(3005, () => console.log('Server Running at http://localhost:3005/'));
  } catch (error) {
    console.log(`DB Error: ${error.message}`);
    process.exit(1);
  }
};

const createTables = async () => {
  try {
    // Create user table
    await database.exec(`
      CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
      );
    `);

    // Create search history table
    await database.exec(`
      CREATE TABLE IF NOT EXISTS search_history (
        search_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        location TEXT,
        weather_data TEXT,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (user_id)
      );
    `);

    console.log("Tables created successfully");
  } catch (error) {
    console.log(`Error creating tables: ${error.message}`);
  }
};

initializeDbAndServer();

// Helper function: Authenticate JWT
const authenticateToken = (request, response, next) => {
  const authHeader = request.headers["authorization"];
  const jwtToken = authHeader && authHeader.split(" ")[1];

  if (!jwtToken) {
    return response.status(401).send("Invalid JWT Token");
  }

  jwt.verify(jwtToken, process.env.JWT_SECRET, (error, payload) => {
    if (error) {
      return response.status(401).send("Invalid JWT Token");
    }
    request.user = payload; // Attach user info to request
    next();
  });
};

// User registration
app.post("/register", async (request, response) => {
  const { username, password } = request.body;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    await database.run(`INSERT INTO user (username, password) VALUES (?, ?);`, [username, hashedPassword]);

    response.status(201).send("User registered successfully");
  } catch (error) {
    if (error.message.includes("UNIQUE constraint failed")) {
      response.status(400).send("Username already exists");
    } else {
      response.status(500).send("Server error");
    }
  }
});

// User login
app.post("/login", async (request, response) => {
  const { username, password } = request.body;
  const user = await database.get(`SELECT * FROM user WHERE username = ?`, [username]);

  if (!user) {
    return response.status(400).send("Invalid user");
  }

  const isPasswordMatched = await bcrypt.compare(password, user.password);
  if (isPasswordMatched) {
    const jwtToken = jwt.sign({ username }, process.env.JWT_SECRET);
    response.send({ jwtToken });
  } else {
    response.status(400).send("Invalid password");
  }
});

// User logout
app.post("/logout", authenticateToken, (request, response) => {
  // As JWT is stateless, there's no need to handle token invalidation on server side.
  response.status(200).send("Logged out successfully");
});

// Update user profile
app.put("/update-profile", authenticateToken, async (request, response) => {
  const { newUsername, newPassword } = request.body;
  const updates = [];
  const params = [];

  if (newUsername) {
    updates.push("username = ?");
    params.push(newUsername);
  }

  if (newPassword) {
    updates.push("password = ?");
    params.push(await bcrypt.hash(newPassword, 10));
  }

  if (updates.length === 0) {
    return response.status(400).send("No update fields provided");
  }

  params.push(request.user.username);

  await database.run(
    `UPDATE user SET ${updates.join(", ")} WHERE username = ?`,
    params
  );

  response.status(200).send("Profile updated successfully");
});

// Get weather data
app.post("/weather", authenticateToken, async (request, response) => {
  const { location, forecast = false } = request.body;
  const apiKey = process.env.WEATHER_API_KEY;

  try {
    const url = forecast
      ? `http://api.openweathermap.org/data/2.5/forecast?q=${location}&appid=${apiKey}&units=metric`
      : `http://api.openweathermap.org/data/2.5/weather?q=${location}&appid=${apiKey}&units=metric`;

    const weatherResponse = await fetch(url);
    const weatherData = await weatherResponse.json();

    if (weatherResponse.status === 200) {
      // Save search history
      await database.run(
        `INSERT INTO search_history (user_id, location, weather_data) 
         SELECT user_id, ?, ? FROM user WHERE username = ?`,
        [location, JSON.stringify(weatherData), request.user.username]
      );
      response.status(200).send(weatherData);
    } else {
      response.status(400).send("Invalid location");
    }
  } catch (error) {
    response.status(500).send("Error fetching weather data");
  }
});

// Get search history
app.get("/history", authenticateToken, async (request, response) => {
  const history = await database.all(
    `SELECT * FROM search_history 
     JOIN user ON user.user_id = search_history.user_id
     WHERE username = ?`,
    [request.user.username]
  );

  response.status(200).send(history);
});

// Delete search history entry
app.delete("/history/:searchId", authenticateToken, async (request, response) => {
  const { searchId } = request.params;
  const result = await database.run(`DELETE FROM search_history WHERE search_id = ?`, [searchId]);

  if (result.changes) {
    response.status(200).send(`Deleted search entry ${searchId}`);
  } else {
    response.status(404).send("Search entry not found");
  }
});
