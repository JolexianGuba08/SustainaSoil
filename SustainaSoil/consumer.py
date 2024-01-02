import asyncio
import json
import requests
from google.cloud.firestore_v1 import FieldFilter, SERVER_TIMESTAMP
from homepage.firestore_db_modules.firestore_database_client import firestore_db
from channels.generic.websocket import AsyncWebsocketConsumer
import time

# for realtime database
firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com/"

# -------------------------------------------- REALTIME DATABASE FUNCTIONS -----------------------------------------------------


# Function to get from rtdb to update firestore
async def update_sensor_data(collection_name, fields_to_update):
    try:
        db = firestore_db()
        response = requests.get(f"{firebase_url}/{collection_name}.json")
        response.raise_for_status()
        data = response.json()

        # Create an array to store documents
        documents_array = []

        # Iterate through the documents in the RTDB
        for document_id, document_data in data.items():
            documents_array.append({
                'document_id': document_id,
                'data': document_data
            })

        # Iterate through the documents_array and update Firestore
        for document in documents_array:
            try:
                package_key = document['data'].get('package_key')

                # Skip documents where 'package_key' is not present
                if package_key is None:
                    continue

                # Extract specific fields to update based on the function
                fields_data = {field: document['data'].get(field, None) for field in fields_to_update}
                fields_data.pop('package_key', None)

                # Exclude 'package_key' from fields_data
                # Get the reference to the Firestore collection
                doc_ref = db.collection(collection_name)

                # Query to filter where to store
                query = doc_ref.where(filter=FieldFilter("package_key", "==", package_key))
                fields_data.pop('package_key', None)
                # Stream results
                docs = query.stream()

                for doc in docs:
                    data = doc.to_dict()
                    # Update the Firestore document
                    doc.reference.update(fields_data)

            except Exception as e:
                print(f"Error updating Firestore: {e}")

        print(f"{collection_name} in Firestore db successfully updated!")
        return True  # Indicate success

    except Exception as e:
        print(f"Error getting data from RTDB: {e}")
        return False  # Indicate failure


    # Replace the function calls with the specific collections and fields you want to update
    collections_and_fields = [
        ("water_level_sensor", ['package_key', 'water_level']),
        ("water_level_sensor_pesticide", ['package_key', 'sensor_id', 'water_level']),
        ("water_flow_sensor", ['flow_rate', 'package_key', 'sensor_id', 'volume_type']),
        ("water_flow_sensor_pesticide", ['flow_rate', 'package_key', 'sensor_id', 'volume_type']),
        ("temperature_humidity_sensor", ['humidity', 'temperature', 'package_key', 'sensor_id']),
        ("soil_moisture_sensor", ['package_key', 'sensor_id', 'moisture_level'])
    ]

    while True:
        for collection_name, fields_to_update in collections_and_fields:
            await update_sensor_data(collection_name, fields_to_update)

async def get_sensor_data(collection_name, package_key, field_name):
    try:
        db = firestore_db()
        # Create a reference to the collection
        collection = db.collection(collection_name)

        # Get the current date and time
        current_date_time = SERVER_TIMESTAMP
        # Create a query against the collection
        query_ref = collection.where(filter=FieldFilter('package_key', '==', package_key))

        # Get the documents in the collection that match the query
        docs = query_ref.get()
        if docs:
            field_value = docs[0].get(field_name)
            return field_value
        return None

    except Exception as e:
        print(f"Error in get_sensor_data: {e}")
        return None


class RealTimeData(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Connected to websocket")

    async def disconnect(self, close_code):
        print("Disconnected from websocket")

    async def update_sensor_data(self):
        await update_sensor_data("temperature_humidity_sensor", ['humidity'])
        await update_sensor_data("temperature_humidity_sensor", ['temperature'])
        await update_sensor_data("soil_moisture_sensor", ['moisture_level'])
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            package_key = data['package_key']

            while True:
                asyncio.create_task(self.update_sensor_data())
                real_time_data = {
                    'soil_moist_sensor': await get_sensor_data('soil_moisture_sensor', package_key, 'moisture_level'),
                    'humidity_sensor': await get_sensor_data('temperature_humidity_sensor', package_key, 'humidity'),
                    'temperature_sensor': await get_sensor_data('temperature_humidity_sensor', package_key, 'temperature'),
                }

                await self.send(text_data=json.dumps({
                    'message': real_time_data
                }))
                # Wait for 2 seconds before fetching data again
                await asyncio.sleep(1)

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
                    'water_level_sensor': await get_sensor_data('water_level_sensor', package_key, 'water_level'),
                    'water_level_sensor_pesticide': await get_sensor_data('water_level_sensor_pesticide', package_key, 'water_level'),
                }

                await self.send(text_data=json.dumps({
                    'message': real_time_data
                }))
                # Wait for 2 seconds before fetching data again
                await asyncio.sleep(1)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        except Exception as e:
            print(f"Error in receive: {e}")
