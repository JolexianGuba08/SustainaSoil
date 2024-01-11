import asyncio
import json
import httpx

import requests
from channels.generic.websocket import AsyncWebsocketConsumer


# -------------------------------------------- REALTIME DATABASE FUNCTIONS -----------------------------------------------------
async def get_sensor_data(collection_name, field_name, package_key):
    try:
        # Construct the URL for the Realtime Database
        firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com/"
        package_key = package_key.strip()
        url = f"{firebase_url}/{collection_name}/{package_key}/{field_name}.json"

        async with httpx.AsyncClient() as client:
            # Make an asynchronous GET request to the RTDB
            response = await client.get(url)

            # Check for HTTP errors
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            if data is None or data == "":
                return False
            # Directly return the JSON data
            return data

    except Exception as e:
        print(f"Error getting data from RTDB: {e}")
        return False  # Indicate failure


class RealTimeData(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Connected to websocket")

    async def disconnect(self, close_code):
        print("Disconnected from websocket")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            package_key = data['package_key']
            while True:
                real_time_data = {
                    'soil_moist_sensor': await get_sensor_data('soil_moisture_sensor', 'moisture_level', package_key),
                    'humidity_sensor': await get_sensor_data('temperature_humidity_sensor', 'humidity', package_key),
                    'temperature_sensor': await get_sensor_data('temperature_humidity_sensor', 'temperature',
                                                                package_key),
                }

                await self.send(text_data=json.dumps({
                    'message': real_time_data
                }))
                # Wait for 2 seconds before fetching data again
                await asyncio.sleep(3)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        except Exception as e:
            print(f"Error in receive: {e}")


class DashBoardRealTime(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Connected to websocket")

    async def disconnect(self, close_code):
        print("Disconnected from websocket")

    async def receive(self, text_data):
        try:
            while True:
                data = json.loads(text_data)
                package_key = data['package_key']

                real_time_data = {
                    'water_level_sensor': await get_sensor_data('water_level_sensor', 'water_level', package_key),
                    'water_level_sensor_pesticide': await get_sensor_data('water_level_sensor_pesticide', 'water_level',
                                                                          package_key, ),
                }
                await self.send(text_data=json.dumps({
                    'message': real_time_data
                }))
                # Wait for 2 seconds before fetching data again
                await asyncio.sleep(2)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        except Exception as e:
            print(f"Error in receive: {e}")


# -------------------------------------------- NOTIFICATION FUNCTIONS -----------------------------------------------------
class GetNotifications(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Connected to notifiction socket")

    async def disconnect(self, close_code):
        print("Disconnected from ")

    async def receive(self, text_data):
        try:
            while True:
                firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com"
                url = f"{firebase_url}/notification/HESUYAM71Wzh_1001.json"

                response = requests.get(url)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    data = response.json()

                    sorted_data = sorted(data.values(), key=lambda x: x['date'], reverse=True)

                    if data:
                        await self.send(text_data=json.dumps({
                            'message': sorted_data,
                            'id': sorted_data
                        }))
                    else:
                        await self.send(text_data=json.dumps({
                            'message': 'No notifications'
                        }))
                else:
                    # Handle the case where the request was not successful
                    print(f"Failed to fetch notification. Status code: {response.status_code}")
                    await self.send(text_data=json.dumps({
                        'message': 'No notifications'
                    }))

                await asyncio.sleep(10)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        except Exception as e:
            print(f"Error in receive: {e}")
