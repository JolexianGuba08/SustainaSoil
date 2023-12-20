from homepage.firestore_db_modules.firestore_database_client import firestore_db
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter
from google.cloud import firestore


# Add Greenery Location
def add_account_greenery_location(email, latitude, longitude):
    db = firestore_db()

    account_greenery_set = {
        'email': email,
        'latitude': latitude,
        'longitude': longitude,
        'date_added': firestore.SERVER_TIMESTAMP,
        'date_modified': firestore.SERVER_TIMESTAMP,
    }

    # Create a reference to the collection
    collection_ref = db.collection('account_greenery')

    # Check if a document with the email already exists
    query = collection_ref.where(filter=FieldFilter('email', '==', email))
    existing_docs = query.get()

    # If there are no existing documents with the email, add a new one
    if not existing_docs:
        # Add a document to the collection
        doc_ref = collection_ref.document()
        doc_ref.set(account_greenery_set)
        # For debugging purposes only! removed later for deployment
        print(f'Account Greenery Location added successfully with ID: {doc_ref.id}')
    else:
        # For debugging purposes only! removed later for deployment
        print(f'A document with email {email} already exists. Not adding a new one.')


# Update Greenery Location
def update_account_greenery_location(email, latitude, longitude):
    db = firestore_db()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    account_greenery_set = {
        'latitude': latitude,
        'longitude': longitude,
        'date_modified': current_datetime
    }

    # Create a reference to the collection
    collection_ref = db.collection('account_greenery')

    # Query for the document based on the email
    query = collection_ref.where(filter=FieldFilter('email', '==', email))
    docs = query.get()

    # Update the document if found
    for doc in docs:
        doc.reference.update(account_greenery_set)
        # For debugging purposes only! removed later for deployment
        print(f'Account Greenery Location for {email} updated successfully')

    # If the document with the email wasn't found, you can handle it here
    if not docs:
        # For debugging purposes only! removed later for deployment
        print(f'No account found with email: {email}')


# Read Greenery Location
def read_account_greenery_location(email):
    db = firestore_db()
    # Create a reference to the collection
    collection_ref = db.collection('account_greenery')

    # Create a query against the collection
    query_ref = collection_ref.where(filter=FieldFilter('email', '==', email))

    # Get the documents in the collection that matches the query
    docs = query_ref.get()

    # For debugging purposes only! removed later for deployment
    print('Account Greenery Location read successfully')
    # It returns a document so all you need to do is to get the data by calling to_dict() in other parts of the code
    return docs

# ---------ADD MORE FUNCTIONS IF NEEDED HERE---------#
