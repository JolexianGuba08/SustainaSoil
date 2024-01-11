from google.cloud.firestore_v1 import FieldFilter

from homepage.firestore_db_modules.firestore_database_client import firestore_db
from google.cloud import firestore
from datetime import datetime, timedelta


def add_forgot_password_session(email, session_id):
    db = firestore_db()

    expiration_seconds = 20 * 60
    expiration_date = datetime.now() + timedelta(seconds=expiration_seconds)
    formatted_expiration_date = expiration_date.strftime("%B %d, %Y at %I:%M:%S %p UTC+8")

    forgot_password_session_set = {
        'session_token': session_id,
        'email': email,
        'date_requested': firestore.SERVER_TIMESTAMP,
        'expiration_date': formatted_expiration_date,
        'expired': False,
    }

    collection_ref = db.collection('forgot_password')
    doc_ref = collection_ref.document()
    doc_ref.set(forgot_password_session_set)

    print(f'Forgot Password Session added successfully with ID: {doc_ref.id}')


def search_forgot_password_session(session_id):
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('forgot_password')

    # Create a query against the collection
    query_ref = collection_ref.where(filter=FieldFilter('session_token', '==', session_id))

    # Retrieve query results
    docs = query_ref.get()

    if not docs:
        return None
    # For debugging purposes only! removed later for deployment
    print(f'Forgot Password session for {session_id} retrieved successfully')

    return docs


def update_forgot_password_session(session_id):
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('forgot_password')

    # Create a query against the collection
    query_ref = collection_ref.where(filter=FieldFilter('session_token', '==', session_id))

    # Retrieve query results
    docs = query_ref.get()

    if not docs:
        return None

    for doc in docs:
        doc.reference.update({
            'expired': True,
        })

    # For debugging purposes only! removed later for deployment
    print(f'Forgot Password session for {session_id} updated successfully')
