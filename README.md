Here’s a template for a comprehensive README file based on your project:

---

# Weather CLI & REST API System

This project is a combination of a Python-based Command-Line Interface (CLI) client and a Node.js REST API server for fetching weather information and managing user data. The system uses JWT for authentication and SQLite for storing user and search history data.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [API Endpoints](#api-endpoints)
5. [Database Schema](#database-schema)
6. [Error Handling](#error-handling)
7. [Known Issues](#known-issues)
8. [Loom Video](#loom-video)

---

## Features

### Python CLI Client:
- **Register** a new user.
- **Login** using username and password to get a JWT token.
- **Logout** and clear the JWT token from the session.
- **Get Current Weather** for a specified location.
- **Get 5-day Forecast** for a specified location.
- **View Search History** of previously queried locations.
- **Delete Search History** by search ID.
- **Update Profile** (username/password).

### Node.js REST API:
- **User Registration**
- **User Login** with JWT token issuance.
- **Weather Data Retrieval** from OpenWeatherMap API.
- **Search History Management** (view, delete).
- **JWT-based Authentication** for secure API access.

---

## Installation

### Prerequisites
- Python 3.x
- Node.js
- SQLite3
- OpenWeatherMap API Key

### Python CLI Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/weather-cli-rest.git
    cd weather-cli-rest/python-cli
    ```


2. Set up the environment variables:
    - Create a `.env` file in the Python CLI directory and add:
    ```bash
    API_BASE_URL=http://localhost:3005
    ```

3. Run the CLI client:
    ```bash
    python cli_client.py
    ```

### Node.js Server Setup
1. Go to the server directory:
    ```bash
    cd weather-cli-rest/node-server
    ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Set up the environment variables:
    - Create a `.env` file in the Node.js directory and add:
    ```bash
    WEATHER_API_KEY=your_openweathermap_api_key
    JWT_SECRET=your_jwt_secret
    ```

4. Start the server:
    ```bash
    node server.js
    ```

---

## Usage

### Python CLI Commands
Run the Python CLI with different commands as shown below.

- **Register**:
    ```bash
    python cli_client.py register <username> <password>
    ```

- **Login**:
    ```bash
    python cli_client.py login <username> <password>
    ```

- **Get Weather**:
    ```bash
    python cli_client.py weather <location>
    ```

- **Get Forecast**:
    ```bash
    python cli_client.py forecast <location>
    ```

- **View History**:
    ```bash
    python cli_client.py history
    ```

- **Delete History**:
    ```bash
    python cli_client.py delete-history <search_id>
    ```

- **Update Profile**:
    ```bash
    python cli_client.py update-profile <new_username> <new_password>
    ```

---

## API Endpoints

| Method | Endpoint                 | Description              | Auth Required |
|--------|--------------------------|--------------------------|---------------|
| POST   | `/register`               | Register a new user      | No            |
| POST   | `/login`                  | Login and get JWT token  | No            |
| POST   | `/logout`                 | Logout user              | Yes           |
| POST   | `/weather`                | Get weather information  | Yes           |
| GET    | `/history`                | Get search history       | Yes           |
| DELETE | `/history/:searchId`      | Delete search entry      | Yes           |
| PUT    | `/update-profile`         | Update user profile      | Yes           |

---

## Database Schema

### Tables

- **User Table** (`user`):
  | Column     | Type    | Description          |
  |------------|---------|----------------------|
  | user_id    | INTEGER | Primary Key (Auto-Inc)|
  | username   | TEXT    | Unique username      |
  | password   | TEXT    | Hashed password      |

- **Search History Table** (`search_history`):
  | Column      | Type    | Description                   |
  |-------------|---------|-------------------------------|
  | search_id   | INTEGER | Primary Key (Auto-Inc)         |
  | user_id     | INTEGER | Foreign Key (User)             |
  | location    | TEXT    | Location queried               |
  | weather_data| TEXT    | Weather data (JSON format)     |
  | search_time | TIMESTAMP| Time of the search            |

---

## Error Handling

- **Invalid JWT Token**: 401 Unauthorized
- **Missing Parameters**: 400 Bad Request
- **Internal Server Error**: 500 Server Error

---
