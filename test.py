import requests
import datetime
import homepage.firestore_db_modules.account_greenery as account_greenery

# email = 'reyalfante0@gmail.com'
# latitude = '10.31028'
# longitude = '123.94944'
#
# account_greenery.add_account_greenery_location(email, latitude, longitude)

#
# def fetch_weather_data(lat, lon, key):
#     url = f'https://api.weatherbit.io/v2.0/forecast/daily?&lat={lat}&lon={lon}&key={key}&days=7'
#     res = requests.get(url)
#     data = res.json()
#     return data
#
#
# def display_weather_info(data):
#     for day_data in data['data']:
#         date = day_data['datetime']
#         # Convert the date string to a datetime object
#         datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
#         # Get the day of the week (0 = Monday, 6 = Sunday)
#         day_of_week = datetime_obj.weekday()
#         # Get the day name corresponding to the day of the week
#         day_name = datetime_obj.strftime('%A')
#         temp = day_data['temp']
#         weather = day_data['weather']['description']
#         print(f"{day_name}: Temperature - {temp} °C  : Weather - {weather}")
#         print(data['city_name'])
#
#
# weather_data = fetch_weather_data('10.31028', '123.94944', '092fc961ff504a4daadc192d6466155b')
# display_weather_info(weather_data)


# import firebase_admin
# from firebase_admin import credentials, storage
# from dotenv import load_dotenv
# import os
# from datetime import datetime, timedelta
#
# load_dotenv()
# start_time = datetime.now()
# # Initialize Firebase Admin SDK
# cred = credentials.Certificate(os.getenv("FIRESTORE_KEY_PATH"))
# firebase_admin.initialize_app(cred, {
#     'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
# })
#
#
# def upload_file_to_firebase(file_path, destination_path):
#     try:
#         bucket = storage.bucket()
#         blob = bucket.blob(destination_path)
#         blob.upload_from_filename(file_path)
#         print(f"File {file_path} uploaded to {destination_path} in Firebase Storage")
#         file_url = get_file_url_from_firebase(destination_path)
#         return file_url, destination_path  # Return both URL and storage path
#     except Exception as e:
#         print(f"Error uploading file: {e}")
#         return None, None
#
#
# def get_file_url_from_firebase(file_path):
#     try:
#         bucket = storage.bucket()
#         blob = bucket.blob(file_path)
#         expiration = datetime.now() + timedelta(days=7)  # Expiration in 7 days (adjust as needed)
#         url = blob.generate_signed_url(expiration=expiration)  # Set the expiration time
#         return url
#     except Exception as e:
#         print(f"Error getting file URL: {e}")
#         return None
#
#
# # Usage example:
# uploaded_file_url, storage_path = upload_file_to_firebase(
#     r"C:\Users\REY\Downloads\279650263_1294819024260510_1850353223875052676_n.jpg",
#     'profile_images/profile.jpg')
# if uploaded_file_url and storage_path:
#     print(f"URL of uploaded file: {uploaded_file_url}")
#     print(f"Storage path for database usage: {storage_path}")
#     # Now, you can pass the URL to your HTML template for display/download
#     # Store the storage_path in your database to reference the file in Firebase Storage
# else:
#     print("File upload failed, URL or storage path not available")
#
# end_time = datetime.now()  # Record the end time
#
# elapsed_time = end_time - start_time  # Calculate the elapsed time
# print(f"Elapsed time: {elapsed_time.total_seconds()} seconds")
# import homepage.firestore_db_modules.cloud_storage as cloud_storage
#
# # get file url from firebase
# file_url = cloud_storage.get_file_url_from_firebase('profile_images/profile_img_back.jpg')
# upload_path = cloud_storage.upload_file_to_firebase(
#     r"C:\Users\REY\Downloads\279650263_1294819024260510_1850353223875052676_n.jpg",
#     'profile_images/profile_img_back.jpg')
# print(upload_path)
# print(file_url)
