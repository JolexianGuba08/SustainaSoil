import requests


# // modify it your needs with version, city, API etc
# http://history.openweathermap.org/data/2.5/history/city?[location]&type=hour&start={start}&cnt={cnt}&appid={YOUR_API_KEY}

def fetch_weather_data(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=7e0f514436e093338b9196987d835e02&units=metric'.format(
        city)
    res = requests.get(url)
    return res.json()


def display_weather_info(data):
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']
    description = data['weather'][0]['description']
    temp = data['main']['temp']

    print('Temperature:', temp, '°C')
    print('Wind:', wind)
    print('Pressure: ', pressure)
    print('Humidity: ', humidity)
    print('Description:', description)


# Get user input for city
city = input("Enter City: ")

# Simulating different times of the day with the same data
print("Morning Weather for", city + ":")
morning_data = fetch_weather_data(city)
display_weather_info(morning_data)
print("\n")

print("Afternoon Weather for", city + ":")
afternoon_data = fetch_weather_data(city)
display_weather_info(afternoon_data)
print("\n")

print("Night Weather for", city + ":")
night_data = fetch_weather_data(city)
display_weather_info(night_data)
