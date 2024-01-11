import requests
import os
import datetime
from dotenv import load_dotenv
from homepage.firestore_db_modules.account_greenery import read_account_greenery_location
from homepage.firestore_db_modules.package_iot import add_package_iot, update_package_iot, read_package_iot

load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY')


# Weather Bit API Docs: https://www.weatherbit.io/api/weather-forecast-16-day

# fetch the weather data
def fetch_weather_data(lat, lon, key=API_KEY):
    print(API_KEY)
    url = f'https://api.weatherbit.io/v2.0/forecast/daily?&lat={lat}&lon={lon}&key={key}&days=7'
    res = requests.get(url)
    data = res.json()
    return data


# get the weather data context
def get_weather_data_context(request):
    if 'session_email' not in request.session and 'session_user_id' not in request.session and 'session_user_type' not in request.session:
        context = {
            'data': 'No data'
        }
        return context

    email = request.session.get('session_email')
    acc_greenery_query = read_account_greenery_location(email)
    if acc_greenery_query is None:
        context = {
            'data': 'No data'
        }
        return context

    latitude, longitude = '', ''
    for doc in acc_greenery_query:
        latitude = doc.to_dict()['latitude']
        longitude = doc.to_dict()['longitude']

    weather_data = fetch_weather_data(latitude, longitude)
    name_city = weather_data['city_name']

    weather_info = {
        'today': [],
        'following_days': []
    }

    # Get current day name
    current_day = datetime.datetime.now().strftime('%A').lower()

    for data in weather_data['data']:
        date = data['datetime']  # for debugging purposes only don't remove
        temp = int(round(data['temp']))
        weather = data['weather']['description']
        weather_icon_code = data['weather']['icon']
        weather_icon = f'https://cdn.weatherbit.io/static/img/icons/{weather_icon_code}.png'

        # Convert the date string to a datetime object
        datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        # Get the day name from the datetime object
        day_name = datetime_obj.strftime('%A').lower()

        # Store temp and weather in the corresponding day list
        if day_name == current_day:
            weather_info['today'].append({
                'date': date,
                'temp': temp,
                'weather': weather.upper(),
                'day_name': day_name.upper(),
            })
        else:
            weather_info['following_days'].append({
                'date': date,
                'temp': temp,
                'weather': weather.upper(),
                'day_name': day_name.upper(),
                'weather_icon': weather_icon
            })

    context = {
        'city_name': name_city,
        'weather_info': weather_info
    }
    return context
