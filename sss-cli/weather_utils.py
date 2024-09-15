def print_weather(weather_data, forecast):
    if forecast:
        print(f"5-day Forecast for {weather_data['city']['name']}:")
        for entry in weather_data['list']:
            print(f"Date: {entry['dt_txt']}")
            print(f"Temperature: {entry['main']['temp']}°C")
            print(f"Weather: {entry['weather'][0]['description']}")
            print("-" * 40)
    else:
        print(f"Current Weather for {weather_data['name']}:")
        print(f"Temperature: {weather_data['main']['temp']}°C")
        print(f"Weather: {weather_data['weather'][0]['description']}")
        print(f"Humidity: {weather_data['main']['humidity']}%")
        print(f"Wind Speed: {weather_data['wind']['speed']} m/s")
