from homepage.firestore_db_modules.firestore_database_client import firestore_db
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter
from google.cloud import firestore


# Add Package IoT
def add_package_iot(package_key, soil_moisture_id, temp_humid_id, flow_sensor_id, water_lvl_id, pump_id):
    db = firestore_db()

    package_iot_set = {
        'package_key': package_key,
        'soil_moisture_id': soil_moisture_id,
        'temp_humid_id': temp_humid_id,
        'water_flow_sensor_id': flow_sensor_id,
        'water_lvl_sensor_id': water_lvl_id,
        'water_pump_id': pump_id,
        'date_added': firestore.SERVER_TIMESTAMP,
        'date_modified': firestore.SERVER_TIMESTAMP,
    }

    # Create a reference to the collection
    collection_ref = db.collection('package')
    # Check if a document with the email already exists
    package_query = collection_ref.where(filter=FieldFilter('package_key', '==', package_key))
    existing_docs = package_query.get()

    # If there are no existing documents with the email, add a new one
    if not existing_docs:
        # Add a document to the collection
        doc_ref = collection_ref.document()
        doc_ref.set(package_iot_set)
        # For debugging purposes only! removed later for deployment
        print(f'Package IoT added successfully with ID: {doc_ref.id}')
    else:
        # For debugging purposes only! removed later for deployment
        print(f'A document with package {package_key} already exists. Not adding a new one.')


# Update Package IoT you may change the parameters if needed
def update_package_iot(package_key, soil_moisture_id, temp_humid_id, flow_sensor_id, water_lvl_id, pump_id):
    db = firestore_db()

    package_iot_set = {
        'package_key': package_key,
        'soil_moisture_id': soil_moisture_id,
        'temp_humid_id': temp_humid_id,
        'water_flow_sensor_id': flow_sensor_id,
        'water_lvl_sensor_id': water_lvl_id,
        'water_pump_id': pump_id,
        'date_modified': firestore.SERVER_TIMESTAMP,
    }

    # Create a reference to the collection
    collection_ref = db.collection('package')

    # Query for the document based on the package key
    query = collection_ref.where(filter=FieldFilter('package_key', '==', package_key))
    docs = query.get()

    # Update the document if found
    for doc in docs:
        doc.reference.update(package_iot_set)
        # For debugging purposes only! removed later for deployment
        print(f'Package IoT {package_key} updated successfully')

    # If the document with the package key wasn't found, you can handle it here
    if not docs:
        # For debugging purposes only! removed later for deployment
        print(f'No package found with package key: {package_key}')


# Read Package IoT
def read_package_iot(package_key):
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('package')

    # Query for the document based on the package key
    query = collection_ref.where(filter=FieldFilter('package_key', '==', package_key))
    docs = query.get()
    # For debugging purposes only! removed later for deployment
    print('Package IOT read successfully')

    # It returns a document so all you need to do is to get the data by calling to_dict() in other parts of the code
    return docs

# ---------ADD MORE FUNCTIONS IF NEEDED HERE---------#
