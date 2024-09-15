import requests
import argparse
import os
from dotenv import load_dotenv
from weather_utils import print_weather
import json

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
TOKEN_FILE = "token.json"

def print_history(history_entries):
    """Format and print history entries."""
    for entry in history_entries:
        print(f"ID: {entry['search_id']}")
        print(f"Location: {entry['location']}")
        print(f"Date: {entry['search_time']}")
        print(f"Weather Data:")
        
        # Handle weather data format
        try:
            weather_data = entry['weather_data']
            if isinstance(weather_data, str):
                # If weather_data is a string, assume it's a JSON string and parse it
                weather_data = json.loads(weather_data)
            print_weather(weather_data, forecast=False)
        except Exception as e:
            print(f"Error displaying weather data: {e}")
        
        print("-" * 40)  # Separator for readability

class CLIClient:
    def __init__(self):
        self.jwt_token = self.load_token()

    def save_token(self, token):
        with open(TOKEN_FILE, 'w') as f:
            json.dump({'token': token}, f)

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                return data.get('token')
        return None

    def clear_token(self):
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    def register(self, username, password):
        response = requests.post(f"{API_BASE_URL}/register", json={"username": username, "password": password})
        if response.status_code == 201:
            print("User registered successfully!")
        else:
            print(f"Registration failed: {response.text}")

    def login(self, username, password):
        response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            self.jwt_token = response.json().get('jwtToken')
            if self.jwt_token:
                self.save_token(self.jwt_token)
                print("Login successful!")
                print(f"JWT Token: {self.jwt_token}")
            else:
                print("Failed to retrieve JWT token.")
        else:
            print(f"Login failed: {response.text}")

    def logout(self):
        if self.jwt_token is None:
            print("Please log in first.")
            return

        response = requests.post(f"{API_BASE_URL}/logout", headers={"Authorization": f"Bearer {self.jwt_token}"})
        if response.status_code == 200:
            self.clear_token()
            self.jwt_token = None
            print("Logged out successfully!")
        else:
            print(f"Logout failed: {response.text}")

    def get_weather(self, location, forecast=False):
        if self.jwt_token is None:
            print("Please log in first.")
            return

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        url = f"{API_BASE_URL}/weather"
        data = {"location": location, "forecast": forecast}

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            weather_data = response.json()
            print_weather(weather_data, forecast)
        else:
            print(f"Weather request failed: {response.text}")

    def get_history(self):
        if self.jwt_token is None:
            print("Please log in first.")
            return

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        url = f"{API_BASE_URL}/history"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            history = response.json()
            if history:
                print("Search History:")
                print_history(history)
            else:
                print("No search history found.")
        else:
            print(f"History request failed: {response.text}")

    def delete_history(self, search_id):
        if self.jwt_token is None:
            print("Please log in first.")
            return

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        url = f"{API_BASE_URL}/history/{search_id}"

        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"Deleted search entry {search_id}")
        else:
            print(f"Delete request failed: {response.text}")

    def update_profile(self, new_username=None, new_password=None):
        if self.jwt_token is None:
            print("Please log in first.")
            return

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        data = {}
        if new_username:
            data['newUsername'] = new_username
        if new_password:
            data['newPassword'] = new_password

        if not data:
            print("Please provide at least a new username or new password.")
            return

        url = f"{API_BASE_URL}/update-profile"
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 200:
            print("Profile updated successfully")
        else:
            print(f"Profile update failed: {response.text}")

if __name__ == "__main__":
    client = CLIClient()

    parser = argparse.ArgumentParser(description="Weather CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register
    register_parser = subparsers.add_parser("register", help="Register a new user")
    register_parser.add_argument("username", help="Username for registration")
    register_parser.add_argument("password", help="Password for registration")

    # Login
    login_parser = subparsers.add_parser("login", help="Login with username and password")
    login_parser.add_argument("username", help="Username for login")
    login_parser.add_argument("password", help="Password for login")

    # Logout
    subparsers.add_parser("logout", help="Logout from the current session")

    # Weather
    weather_parser = subparsers.add_parser("weather", help="Get current weather information for a location")
    weather_parser.add_argument("location", help="Location for weather information")

    # Forecast
    forecast_parser = subparsers.add_parser("forecast", help="Get a 5-day weather forecast for a location")
    forecast_parser.add_argument("location", help="Location for weather forecast")

    # History
    subparsers.add_parser("history", help="Get search history")

    # Delete History
    delete_history_parser = subparsers.add_parser("delete-history", help="Delete a specific search history entry")
    delete_history_parser.add_argument("search_id", help="ID of the search history entry to delete")

    # Update Profile
    update_profile_parser = subparsers.add_parser("update-profile", help="Update profile information")
    update_profile_parser.add_argument("new_username", help="New username")
    update_profile_parser.add_argument("new_password", help="New password")

    args = parser.parse_args()

    if args.command == "register":
        client.register(args.username, args.password)
    elif args.command == "login":
        client.login(args.username, args.password)
    elif args.command == "logout":
        client.logout()
    elif args.command == "weather":
        client.get_weather(args.location, forecast=False)
    elif args.command == "forecast":
        client.get_weather(args.location, forecast=True)
    elif args.command == "history":
        client.get_history()
    elif args.command == "delete-history":
        client.delete_history(args.search_id)
    elif args.command == "update-profile":
        client.update_profile(args.new_username, args.new_password)
    else:
        parser.print_help()
