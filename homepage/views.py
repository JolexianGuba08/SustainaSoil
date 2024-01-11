import json
import uuid

import bcrypt
from django.contrib.sites import requests
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.urls import reverse
from django.views.decorators.http import require_POST

from homepage.firestore_db_modules.realtime_database_connection import update_water_scheduling, update_parameter, \
    turning_on_off, pesticide_now, update_notification_type, water_now
# Other imports...
from homepage.forms import EditProfileForm, ChangePasswordForm
from homepage.models import Packages, Account_Package, Account, Account_Plants, Plants, Account_Plant_Preferences
from homepage.user_context.context_processor import user_context
import homepage.firestore_db_modules.cloud_storage as cloud_storage
import homepage.firestore_db_modules.account_greenery as account_greenery
from homepage.weather_api import get_weather_data_context
from homepage.firestore_db_modules.create_forum_post import *
from homepage.firestore_db_modules.create_forum_comment import *


# Create your views here.
def homepage(request):
    if 'session_email' not in request.session and 'session_user_id' not in request.session and 'session_user_type' not in request.session:
        return redirect('login_page')
    acc_package = Account_Package.objects.filter(user_id=request.session.get('session_user_id')).first()
    # context = get_weather_data_context(request)
    if acc_package:
        return render(request, 'dashboard_page/user-dashboard.html', {'package_key': acc_package})
    else:
        return render(request, 'dashboard_page/user-dashboard.html')


def process_location(request):
    if 'session_email' not in request.session and 'session_user_id' not in request.session and 'session_user_type' not in request.session:
        return redirect('login_page')

    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Set session variables
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        return JsonResponse({'message': 'Location received successfully'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


def preloader(request):
    return render(request, 'preloader.html')


def web_notif(request):
    return render(request, 'web_notification.html')


def mobile_notif(request):
    return render(request, 'mobile_notification.html')


# Profile Views
def profile(request):
    context_data = user_context(request)

    # Pass the context data when initializing the form
    form = EditProfileForm(request=request, initial=context_data)
    forms = ChangePasswordForm()
    return render(request, 'profile_page/user-profile.html', {'form': form, 'forms': forms})


def overview(request):
    return render(request, 'profile_page/include_overview.html')


def get_profile_value(request):
    user_id = request.session.get('session_user_id')

    try:
        user = Account.objects.get(acc_id=user_id)

        # Serialize the user data into a dictionary
        serialized_user = serializers.serialize('python', [user])
        user_data = serialized_user[0]['fields']

        # Extract required fields
        context = {
            'first_name': user_data['acc_first_name'],
            'last_name': user_data['acc_last_name'],
            'contact_number': user_data['acc_phone'] if user_data['acc_phone'] else '',
        }

        return JsonResponse(context)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)


# Greenery Views
# Adding location or package
def greenery(request):
    hasPackage = False
    try:

        account_package = Account_Package.objects.filter(user_id=request.session.get('session_user_id'))

        if account_package:
            hasPackage = True
            return render(request, 'greenery_page/user-greenery.html', {'account_package': account_package,
                                                                        'package_key': account_package,
                                                                        'hasPackage': hasPackage})
    except Account_Package.DoesNotExist:
        return render(request, 'greenery_page/user-greenery.html', {'hasPackage': hasPackage})


def check_package_id(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        print(package_id)
        try:
            package_id = Packages.objects.get(package_key=package_id).pk
            if package_id:
                package_id_exist = Account_Package.objects.filter(package_key=package_id).first()
                if not package_id_exist:
                    return JsonResponse({'status': 'True', 'message': 'Package successfully registered. Thank you!'})
                else:
                    return JsonResponse({'status': 'False', 'message': 'Package is already registered.'})
        except Packages.DoesNotExist:
            return JsonResponse({'status': "Error", 'message': 'Package does not exist'})

    return render(request, 'greenery_page/add-plant.html')


def add_package(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        package_name = request.POST.get('package_name')
        package_location = request.POST.get('location')
        long = request.POST.get('long')
        lat = request.POST.get('lat')
        user_email = request.session.get('session_email')
        existing_acc = account_greenery.read_account_greenery_location(user_email)
        try:
            package_key = Packages.objects.get(package_key=package_id)
            email = Account.objects.get(acc_email=user_email)

            if package_key:
                package_id_exist = Account_Package.objects.filter(package_key=package_id).first()
                if not package_id_exist:
                    if not package_location == "None" and lat == "None" and long == "None" and not existing_acc:
                        account_greenery.add_account_greenery_location(user_email, lat, long, package_location)
                    Account_Package.objects.create(acc_package_name=package_name, package_key=package_key,
                                                   user_id=email)
                    add_plant_url = reverse("add_plant", kwargs={'package_key': package_key})
                    return JsonResponse(
                        {'status': 'True', 'message': 'Package added successfully', 'redirect_to': add_plant_url})
                else:
                    return JsonResponse({'status': 'False', 'message': 'Package is already registered.'})
        except Packages.DoesNotExist:
            return JsonResponse({'error': 'Package does not exist'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'Error on registering package {e}'})


def add_plant(request, package_key):
    global plant_img, package_name
    plant_img = None
    package_name = None

    try:
        package_name = Account_Package.objects.get(package_key=package_key)
        package_name = package_name.acc_package_name

    except Account_Package.DoesNotExist:
        # Handle the case where the object is not found
        package_name = None

    try:

        account_plant = Account_Plants.objects.filter(
            package_key=package_key,
            user_id=request.session.get('session_user_id')
        )

        slot = Account_Plants.objects.get(
            package_key=package_key,
            user_id=request.session.get('session_user_id')
        ).package_key.package_slot

        acc_count = account_plant.count()
        print(slot, "slot")
        print(acc_count, "acc_count")
        account_plants = Account_Plants.objects.filter(user_id=request.session.get('session_user_id'))
        if account_plants:
            for account_plants in account_plants:
                plant_img = cloud_storage.get_file_url_from_firebase(account_plants.plant_id.plant_image)
            if slot >= acc_count:
                hasSlot = False
            else:
                hasSlot = True

    except Account_Plants.DoesNotExist:
        # Handle the case where the object is not found
        hasSlot = True
        account_plant = None

    return render(request, 'greenery_page/add-plant.html', {
        'hasSlot': hasSlot,
        'account_plants': account_plant,
        'package_key': package_key,
        'plant_img': plant_img,
        'package_name': package_name
    })


# add location end point
def get_location(request):
    if request.method == 'POST':
        lat = request.POST.get('latitude')
        long = request.POST.get('longitude')
        api_key = '658e1f6cbb4d1447580277gspecb10a'

        if long and lat:
            api_url = f'https://geocode.maps.co/reverse?lat={lat}&lon={long}&api_key={api_key}'
            # Use requests.get to make the HTTP request
            response = requests.get(api_url)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Assuming the response contains JSON data
                data = response.json()
                print(data['display_name'])
                return JsonResponse({'message': 'Location received successfully', 'location': data['display_name']})
            else:
                return JsonResponse({'message': 'Failed to get location', 'status_code': response.status_code})
        else:
            return JsonResponse({'message': 'Latitude and longitude parameters are required'})


def presets(request, package_key):
    plants = Plants.objects.all()

    if plants:
        for plant in plants:
            # Adding the image URL to each plant object
            plant.plant_image_url = cloud_storage.get_file_url_from_firebase(plant.plant_image)

        print(plants)  # Adding the plant preferences to each plant objec
        return render(request, 'greenery_page/user-presets.html',
                      {'plants': plants, 'package_key': package_key})

    return render(request, 'greenery_page/user-presets.html', {'package_key': package_key})


def get_sensor_data(collection_name, package_keys):
    try:
        firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com"

        results = {}

        for package_key in package_keys:
            # Construct the URL for the Realtime Database
            package_key = package_key.strip()
            url = f"{firebase_url}/{collection_name}/{package_key}/.json"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                results = data
            else:
                results = None

        return results

    except Exception as e:
        print(f"Error getting data from RTDB: {e}")
        return False


def plant_profile(request, package_key, plant_id):
    user_id = request.session.get('session_user_id')
    # Check if Account_Plants object exists
    exist = Account_Plants.objects.filter(
        plant_id=plant_id,
        user_id=user_id,
        package_key=package_key
    ).exists()
    take_cared = exist
    # Retrieve the Plants object based on plant_id
    plants = get_object_or_404(Plants, pk=plant_id)
    plant_image_url = cloud_storage.get_file_url_from_firebase(plants.plant_image)

    try:
        acc_plant = Account_Plants.objects.get(
            plant_id=plant_id,
            user_id=user_id,
            package_key=package_key
        )
    except Account_Plants.DoesNotExist:
        # Handle the case where the object is not found
        acc_plant = None

    try:
        water_schedule_data = get_sensor_data('schedule_water', [package_key])
        pesc_schedule_data = get_sensor_data('schedule_pesticide', [package_key])

        water_data = {
            'am_pm_value': water_schedule_data.get('am_pm', ""),
            'hours_value': (int(water_schedule_data.get('hours')) + 12) % 24 if water_schedule_data.get(
                'am_pm') == 'pm' else str(water_schedule_data.get('hours')),
            'minutes_value': int(water_schedule_data.get('minutes')) if water_schedule_data.get('minutes') else "",
            'mon': 'true' if water_schedule_data.get('mon') else 'false',
            'tue': 'true' if water_schedule_data.get('tue') else 'false',
            'wed': 'true' if water_schedule_data.get('wed') else 'false',
            'thu': 'true' if water_schedule_data.get('thu') else 'false',
            'fri': 'true' if water_schedule_data.get('fri') else 'false',
            'sat': 'true' if water_schedule_data.get('sat') else 'false',
            'sun': 'true' if water_schedule_data.get('sun') else 'false',
            'isSchedule': 'true' if water_schedule_data.get('isSchedule') else 'false',
        }

        pesc_data = {
            'am_pm_value': pesc_schedule_data.get('am_pm', ""),
            'hours_value': (int(pesc_schedule_data.get('hours')) + 12) % 24 if pesc_schedule_data.get(
                'am_pm') == 'pm' else str(pesc_schedule_data.get('hours')),
            'minutes_value': int(pesc_schedule_data.get('minutes')) if pesc_schedule_data.get('minutes') else "",
            'mon': 'true' if pesc_schedule_data.get('mon') else 'false',
            'tue': 'true' if pesc_schedule_data.get('tue') else 'false',
            'wed': 'true' if pesc_schedule_data.get('wed') else 'false',
            'thu': 'true' if pesc_schedule_data.get('thu') else 'false',
            'fri': 'true' if pesc_schedule_data.get('fri') else 'false',
            'sat': 'true' if pesc_schedule_data.get('sat') else 'false',
            'sun': 'true' if pesc_schedule_data.get('sun') else 'false',
            'isSchedule': 'true' if pesc_schedule_data.get('isSchedule') else 'false',
        }

    except Exception as e:
        print(e)
        water_data = None
        pesc_data = None
    return render(
        request,
        'greenery_page/plant-profile.html',
        {
            'plants': plants,
            'package_key': package_key,
            'take_cared': take_cared,
            'acc_plant': acc_plant,
            'plant_image_url': plant_image_url,
            'water_data': water_data,
            'pesc_data': pesc_data
        }
    )


def take_care_plant(request):
    if request.method == 'POST':
        user_id = request.session.get('session_user_id')
        package_key = request.POST.get('package_key')
        plant_id = request.POST.get('plant_id')
        try:
            plant = Plants.objects.get(pk=plant_id)
            user_id = Account.objects.get(pk=user_id)
            acc_package = Account_Package.objects.get(package_key=package_key, user_id=user_id)
            acc_preferences = Account_Plant_Preferences.objects.create(
                acc_plant_min_temp=plant.plant_pref_id.plant_min_temp,
                acc_plant_max_temp=plant.plant_pref_id.plant_max_temp,
                acc_plant_min_moist_lvl=plant.plant_pref_id.plant_min_moist_lvl,
                acc_plant_max_moist_lvl=plant.plant_pref_id.plant_max_moist_lvl)

            Account_Plants.objects.create(plant_id=plant,
                                          user_id=acc_package.user_id,
                                          package_key=acc_package.package_key,
                                          acc_plant_pref_id=acc_preferences)
            return JsonResponse({'message': 'Plant taken cared successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'{e}'})


def save_acc_preferences(request):
    if request.method == 'POST':
        user_id = request.session.get('session_user_id')
        package_key = request.POST.get('package_key')
        plant_id = request.POST.get('plant_id')
        min_temp = request.POST.get('min_temp')
        max_temp = request.POST.get('max_temp')
        min_moist = request.POST.get('min_moist')
        max_moist = request.POST.get('max_moist')
        print(user_id, package_key, plant_id, min_temp, max_temp, min_moist, max_moist)
        try:
            plant = Plants.objects.get(pk=plant_id)
            user_id = Account.objects.get(pk=user_id)
            acc_package = Account_Plants.objects.get(package_key=package_key, user_id=user_id, plant_id=plant)
            acc_package.acc_plant_pref_id.acc_plant_min_temp = min_temp
            acc_package.acc_plant_pref_id.acc_plant_max_temp = max_temp
            acc_package.acc_plant_pref_id.acc_plant_min_moist_lvl = min_moist
            acc_package.acc_plant_pref_id.acc_plant_max_moist_lvl = max_moist
            acc_package.acc_plant_pref_id.save()
            update_parameter('parameters', package_key, max_moist, max_temp, min_moist, min_temp)

            return JsonResponse({'message': 'User preferences updated successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'{e}'})


def set_default_values(request):
    print("setting to default values")
    if request.method == 'POST':
        user_id = request.session.get('session_user_id')
        package_key = request.POST.get('package_key')
        plant_id = request.POST.get('plant_id')
        try:
            plant = Plants.objects.get(pk=plant_id)
            user_id = Account.objects.get(pk=user_id)
            acc_package = Account_Plants.objects.get(package_key=package_key, user_id=user_id, plant_id=plant)
            acc_package.acc_plant_pref_id.acc_plant_min_temp = plant.plant_pref_id.plant_min_temp
            acc_package.acc_plant_pref_id.acc_plant_max_temp = plant.plant_pref_id.plant_max_temp
            acc_package.acc_plant_pref_id.acc_plant_min_moist_lvl = plant.plant_pref_id.plant_min_moist_lvl
            acc_package.acc_plant_pref_id.acc_plant_max_moist_lvl = plant.plant_pref_id.plant_max_moist_lvl
            acc_package.acc_plant_pref_id.save()
            update_parameter('parameters', package_key, plant.plant_pref_id.plant_max_moist_lvl,
                             plant.plant_pref_id.plant_max_temp, plant.plant_pref_id.plant_min_moist_lvl,
                             plant.plant_pref_id.plant_min_temp)

            return JsonResponse({'message': 'Set to default values successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'{e}'})


def water_scheduling(request, package_key):
    try:
        am_pm_value = request.POST.get('am_pm_value')
        selected_days = request.POST.get('selected_days')
        hour_input = request.POST.get('hour_input')
        minutes_input = request.POST.get('minutes_input')
        schedule_type = request.POST.get('schedule_type')
        isDaily = False
        if am_pm_value == "pm":
            hour_input = (int(hour_input) + 12) % 24
            hour_input = str(hour_input)

        week_days_dict = {
            "sun": False,
            "mon": False,
            "tue": False,
            "wed": False,
            "thu": False,
            "fri": False,
            "sat": False,
        }
        if all(value is False for value in week_days_dict.values()):
            isDaily = True

        # Set the days to True based on the provided list
        for day in week_days_dict:
            week_days_dict[day] = day.lower() in selected_days

        if schedule_type == "watering":
            schedule_type = "schedule_water"
            message = "Watering schedule saved successfully"
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input,
                                                      week_days_dict, schedule_type, isDaily)
            if return_response["status"] == "success":
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save watering schedule"
                return JsonResponse({'status': 'error', 'message': message})

        else:

            schedule_type = "schedule_pesticide"
            message = "Pestecide schedule saved successfully"
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input,
                                                      week_days_dict, schedule_type, isDaily)
            if return_response["status"] == "success":
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save pestecide schedule"
                return JsonResponse({'status': 'error', 'message': message})
        return JsonResponse({'message': message})
    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})


def schedule_on_off(request, package_key):
    try:
        is_on = request.POST.get('isSchedule')
        schedule_type = request.POST.get('schedule_type')
        print(schedule_type)
        if is_on == "true":
            is_on = True
        else:
            is_on = False

        if schedule_type == "watering":
            schedule_type = "schedule_water"
            return_response = turning_on_off(schedule_type, package_key, is_on)
            if return_response["status"] == "success":
                message = "Watering " + return_response["message"]
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save watering schedule"
                return JsonResponse({'status': 'error', 'message': message})

        else:
            schedule_type = "schedule_pesticide"
            return_response = turning_on_off(schedule_type, package_key, is_on)
            if return_response["status"] == "success":
                message = "Pestecide " + return_response["message"]
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save pestecide schedule"
                return JsonResponse({'status': 'error', 'message': message})

    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})


def schedule_reset(request, package_key):
    try:
        am_pm_value = ""
        hour_input = ""
        minutes_input = ""
        schedule_type = request.POST.get('schedule_type')
        isDaily = False

        week_days_dict = {
            "sun": False,
            "mon": False,
            "tue": False,
            "wed": False,
            "thu": False,
            "fri": False,
            "sat": False,
        }
        is_on = False

        if schedule_type == "watering":
            schedule_type = "schedule_water"
            message = "Reset schedule saved successfully"
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input,
                                                      week_days_dict, schedule_type, isDaily)
            turnoff = turning_on_off(schedule_type, package_key, is_on)
            if return_response["status"] == "success":
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save watering schedule"
                return JsonResponse({'status': 'error', 'message': message})

        else:
            schedule_type = "schedule_pesticide"
            message = "Reset schedule saved successfully"
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input,
                                                      week_days_dict, schedule_type, isDaily)
            turnoff = turning_on_off(schedule_type, package_key, is_on)

            if return_response["status"] == "success":
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save pestecide schedule"
                return JsonResponse({'status': 'error', 'message': message})
        return JsonResponse({'message': message})
    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})

def water_now_button(request,package_key):
    notif_id = request.GET.get('notif_id')
    try:
        print(notif_id,package_key)
        if notif_id:
          update_notification_type(package_key,notif_id)

        response = water_now(package_key)
        if response["status"] == "success":
            print(response["status"])
            message = "Watering now"
            return JsonResponse({'message': message})
        elif response["status"] == "false":
            message = "Currently Watering"
            return JsonResponse({'message': message})

    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})

def pesc_now(request ,package_key):
    notif_id = request.GET.get('notif_id')
    try:
        if notif_id:
           update_notification_type(package_key,notif_id)

        response = pesticide_now(package_key)
        if response["status"] == "success":
            message = "Apply pesticide now"
            return JsonResponse({'message': message})
        elif response["status"] == "false":
            message = "Currently Applying Pesticide"
            return JsonResponse({'message': message})

    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})

def cancel_now(request,package_key):
    notif_id = request.GET.get('notif_id')
    try:

        response = update_notification_type(package_key,notif_id)

        if response["status"] == "success":
            message = "Cancel now"
            return JsonResponse({'message': message})
        elif response["status"] == "false":
            message = "Failed to cancel"
            return JsonResponse({'message': message})

    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})

# Includes Plant Profile Views
def parameter_form(request):
    return render(request, 'greenery_page/include_plant_profile/parameter_form.html')


@require_POST
def update_profile(request):
    try:
        account = Account.objects.get(acc_id=request.session.get('session_user_id'))

        # Get form data
        first_name = request.POST.get('acc_first_name')
        last_name = request.POST.get('acc_last_name')
        contact = request.POST.get('acc_phone')
        profile_pic = request.FILES.get('profile_pic')
        background_img = request.FILES.get('background_img')
        print(first_name, last_name, contact, profile_pic, background_img)

        # Update account fields if form data is present
        if first_name:
            account.acc_first_name = first_name
        if last_name:
            account.acc_last_name = last_name
        if contact:
            account.acc_phone = contact

        # Process and save profile pic if available
        if profile_pic:
            fs = FileSystemStorage(location='homepage/temp/profile/')
            filename = fs.save(profile_pic.name, profile_pic)

            # Get the complete storage path of the saved file
            file_path = fs.path(filename)
            # create a random file name

            upload_image = cloud_storage.upload_file_to_firebase(file_path,
                                                                 f'profile_images/{generate_filename(account.acc_id)}')

            account.acc_profile_img = upload_image

            # Delete the temporary file after successful upload
            fs.delete(filename)

        # Process and save background image if available
        if background_img:
            fs = FileSystemStorage(location='homepage/temp/background/')
            filename = fs.save(background_img.name, background_img)

            # Get the complete storage path of the saved file
            file_path = fs.path(filename)
            # create a random file name

            upload_image_back = cloud_storage.upload_file_to_firebase(file_path,
                                                                      f'background_images/{generate_filename(account.acc_id)}')

            account.acc_background_img = upload_image_back

            # Delete the temporary file after successful upload
            fs.delete(filename)

        account.save()
        return JsonResponse({'success': True})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'errors': 'User profile not found or error occurred'})


def generate_filename(user_id):
    # Generate a random UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4().hex

    # Combine the random UUID with the user ID
    filename = f"{user_id}_{unique_id}"

    return filename


@require_POST
def check_password(request):
    try:
        if request.method == 'POST':
            user_id = request.session.get('session_user_id')
            password = request.POST.get('old_password')
            account = Account.objects.get(acc_id=user_id)
            if bcrypt.checkpw(password.encode('utf8'), account.acc_password.encode('utf8')):
                return JsonResponse({'success': True, 'message': 'Password matched successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Password does not match'})
    except Account.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User account not found'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})


@require_POST
def change_password(request):
    try:
        if request.method == 'POST':
            new_password = request.POST.get('acc_new_password')
            confirm_password = request.POST.get('acc_confirm_password')
            print(new_password, confirm_password)
            password = str(new_password)
            if new_password != confirm_password:
                return JsonResponse({'success': False, 'errors': 'Password does not match'})

            account = Account.objects.get(acc_id=request.session.get('session_user_id'))
            account.acc_password = password
            account.save()

            return JsonResponse({'success': True})
    except Account.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User account not found'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'})


def get_user_data(user_id):
    account = Account.objects.get(acc_id=user_id)

    # Serialize the user data into a dictionary
    serialized_user = serializers.serialize('python', [account])
    user_data = serialized_user[0]['fields']
    profile_img = cloud_storage.get_file_url_from_firebase(user_data['acc_profile_img'])
    # Extract required fields
    context = {
        'first_name': user_data['acc_first_name'],
        'last_name': user_data['acc_last_name'],
        'profile_image': profile_img,
        'email': user_data['acc_email'],
    }

    return context


# def forums(request):
#     data = get_all_posts()
#
#     # Loop through the data and access each post
#     for post in data:
#         # Get the user id of the post
#         user_id = post['user_id']
#         attachment = post['attachment']
#
#         # Request a link from the firebase storage if there's an attachment
#         if attachment:
#             attachment = cloud_storage.get_file_url_from_firebase(attachment)
#             post['attachment'] = attachment
#
#         # Get the user data using the user id
#         user_data = get_user_data(user_id)
#
#         # Add the user data to the post
#         post['user_data'] = user_data
#
#         # Get the comments of the post using the post_id
#         post_id = post['post_id']
#         comments = get_all_comments(post_id)
#
#         # Add the comments to the post
#         post['comments'] = comments
#
#         # Add user data to each comment
#         for comment in comments:
#             # Get the user id of the comment
#             user_id = comment['user_id']
#
#             # Get the user data using the user id
#             user_data = get_user_data(user_id)
#
#             # Add the user data to the comment
#             comment['user_data'] = user_data
#
#     return render(request, 'forum_page/user-forum.html', {'posts': data})
def forums(request):
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('forum_posts')

    # Create a query against the collection
    query_ref = collection_ref.order_by('date_added', direction=firestore.Query.DESCENDING)

    # Retrieve all documents
    docs = query_ref.stream()

    posts = []

    for doc in docs:
        post_data = doc.to_dict()
        user_id = post_data['user_id']
        post_id = post_data['post_id']

        # Request a link from Firebase storage if there's an attachment
        if post_data['attachment']:
            post_data['attachment'] = cloud_storage.get_file_url_from_firebase(post_data['attachment'])

        # Get the user data using the user id
        user_data = get_user_data(user_id)

        # Add the user data to the post
        post_data['user_data'] = user_data

        # Get the comments of the post using the post_id
        comments = get_all_comments(post_id)

        # Add the comments to the post
        post_data['comments'] = comments

        # Add user data to each comment
        for comment in comments:
            # Get the user id of the comment
            comment_user_id = comment['user_id']

            # Get the user data using the user id
            comment_user_data = get_user_data(comment_user_id)

            # Add the user data to the comment
            comment['user_data'] = comment_user_data

        posts.append(post_data)

    return render(request, 'forum_page/user-forum.html', {'posts': posts})


def view_comment_forums(request):
    return render(request, 'forum_page/view-comments.html')


def generate_post_id(user_id):
    # Generate a random UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4().hex

    # Combine the random UUID with the user ID
    post_id = f"{user_id}_{unique_id}"

    return post_id


def create_forum_post(request):
    # Get the text content and attachment from the request
    text_content = request.POST.get('text-content')
    attachment = request.FILES.get('attachment')
    acc_id = request.session.get('session_user_id')

    # Check if text content is provided
    if not text_content:
        return JsonResponse({'success': False, 'error': 'Please provide a text content'})
    else:
        # Check if an attachment is provided
        is_attachment = False
        if attachment:
            is_attachment = True

            # Save the attachment to a temporary location
            fs = FileSystemStorage(location='homepage/temp/forums/')
            filename = fs.save(attachment.name, attachment)
            file_path = fs.path(filename)

            # Upload the attachment to Firebase and get the URL
            attachment = cloud_storage.upload_file_to_firebase(file_path, f'forum_posts/{generate_filename(acc_id)}')

            # Delete the temporary file
            fs.delete(filename)
        else:
            attachment = None

        # Generate a post ID and create the forum post
        post_id = generate_post_id(acc_id)
        create_post_forum(post_id, acc_id, attachment, is_attachment, text_content)

        return JsonResponse({'success': True, 'message': 'Post created successfully'})


def generate_comment_id(user_id):
    # Generate a random UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4().hex
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Combine the random UUID with the user ID
    comment_id = f"{user_id}_{unique_id}_{date}"

    return comment_id


def create_forum_comment(request):
    # Get the text content and attachment from the request
    comment = request.POST.get('comment')
    post_id = request.POST.get('post_id')
    acc_id = request.session.get('session_user_id')
    # Check if text content is provided
    if not comment:
        return JsonResponse({'success': False, 'error': 'Please provide a text content'})
    comment_id = generate_comment_id(acc_id)
    create_comment_forum(comment_id, comment, post_id, acc_id)
    return JsonResponse({'success': True, 'message': 'Comment created successfully'})


