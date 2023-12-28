import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv("FIRESTORE_KEY_PATH"))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})


# for uploading the file and return the path
def upload_file_to_firebase(file_path, destination_path):
    try:
        bucket = storage.bucket()  # get the bucket
        blob = bucket.blob(destination_path)  # get the blob
        blob.upload_from_filename(file_path)  # upload the file
        print(f"File {file_path} uploaded to {destination_path} in Firebase Storage")
        return destination_path
    except Exception as e:
        print(f"Error uploading file: {e}")


# for downloading the file from firebase this is for testing purpose
def download_file_from_firebase(source_path, destination_path):
    try:
        bucket = storage.bucket()  # get the bucket
        blob = bucket.blob(source_path)  # get the blob
        blob.download_to_filename(destination_path)  # download the file
        print(f"File {source_path} downloaded to {destination_path} from Firebase Storage")
    except Exception as e:
        print(f"Error downloading file: {e}")


# Locate the file and get the link
def get_file_url_from_firebase(file_path):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        expiration = datetime.now() + timedelta(days=7)
        url = blob.generate_signed_url(expiration=expiration)
        return url
    except Exception as e:
        print(f"Error getting file URL: {e}")
        return None
