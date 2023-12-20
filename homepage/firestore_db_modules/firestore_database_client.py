import os

from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()


# Firestore Database Documentation: https://firebase.google.com/docs/firestore

def firestore_db():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("FIRESTORE_KEY_PATH")
    # Initialize Firestore client
    db = firestore.Client()
    return db
