import requests
import datetime


def fetch_weather_data(lat, lon, key):
    url = f'https://api.weatherbit.io/v2.0/forecast/daily?&lat={lat}&lon={lon}&key={key}&days=7'
    res = requests.get(url)
    data = res.json()
    return data


def display_weather_info(data):
    for day_data in data['data']:
        date = day_data['datetime']
        # Convert the date string to a datetime object
        datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        # Get the day of the week (0 = Monday, 6 = Sunday)
        day_of_week = datetime_obj.weekday()
        # Get the day name corresponding to the day of the week
        day_name = datetime_obj.strftime('%A')
        temp = day_data['temp']
        weather = day_data['weather']['description']
        print(f"{day_name}: Temperature - {temp} °C  : Weather - {weather}")


weather_data = fetch_weather_data('10.31028', '123.94944', '092fc961ff504a4daadc192d6466155b')
display_weather_info(weather_data)
