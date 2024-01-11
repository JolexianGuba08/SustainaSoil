import json

from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.urls import reverse

from homepage.firestore_db_modules.realtime_database_connection import update_water_scheduling, update_parameter, \
    turning_on_off, get_notification
# Other imports...
from homepage.forms import EditProfileForm
from homepage.models import Packages, Account_Package, Account, Account_Plants, Plants, Account_Plant_Preferences
from homepage.user_context.context_processor import user_context
import homepage.firestore_db_modules.cloud_storage as cloud_storage
import homepage.firestore_db_modules.account_greenery as account_greenery

# Create your views here.
def homepage(request):
    if 'session_email' not in request.session and 'session_user_id' not in request.session and 'session_user_type' not in request.session:
        return redirect('login_page')
    acc_package = Account_Package.objects.filter(user_id=request.session.get('session_user_id')).first().package_key

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
    # get file url from firebase
    file_url = cloud_storage.get_file_url_from_firebase('profile_images/default_back_img.png')

    print(file_url)
    # Fetch the context data using your user_context function
    context_data = user_context(request)

    # Pass the context data when initializing the form
    form = EditProfileForm(request=request, initial=context_data)
    return render(request, 'profile_page/user-profile.html', {'form': form})


def overview(request):
    return render(request, 'profile_page/include_overview.html')


def edit_profile(request):
    if request.method == 'POST':

        form = EditProfileForm(request.POST)
        if form.is_valid():
            print('Form is valid')
            return redirect('profile')
        else:
            print('Form is not valid')
            return redirect('edit_profile')
    else:
        return render(request, 'profile_page/include_edit_profile.html', {'form': EditProfileForm()})


def change_password(request):
    return render(request, 'profile_page/include_change_password.html')


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
            package_id = Packages.objects.get(package_key = package_id).pk
            if package_id:
                package_id_exist = Account_Package.objects.filter(package_key = package_id).first()
                if not package_id_exist:
                    return JsonResponse({'status':'True','message':'Package successfully registered. Thank you!'})
                else:
                    return JsonResponse({'status':'False','message':'Package is already registered.'})
        except Packages.DoesNotExist:
            return JsonResponse({'status':"Error",'message':'Package does not exist'})

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
                    return JsonResponse({'status':'True','message': 'Package added successfully','redirect_to': add_plant_url})
                else:
                    return JsonResponse({'status':'False','message': 'Package is already registered.'})
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
            update_parameter('parameters', package_key, plant.plant_pref_id.plant_max_moist_lvl, plant.plant_pref_id.plant_max_temp, plant.plant_pref_id.plant_min_moist_lvl, plant.plant_pref_id.plant_min_temp)

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
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input, week_days_dict, schedule_type,isDaily)
            if return_response["status"] == "success":
                return JsonResponse({'message':message})
            elif return_response["status"] == "error":
                message = "Failed to save watering schedule"
                return JsonResponse({'status':'error','message': message})

        else:

            schedule_type = "schedule_pesticide"
            message = "Pestecide schedule saved successfully"
            return_response = update_water_scheduling(package_key, am_pm_value, hour_input, minutes_input, week_days_dict, schedule_type,isDaily)
            if return_response["status"] == "success":
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save pestecide schedule"
                return JsonResponse({'status':'error', 'message': message})
        return JsonResponse({'message': message})
    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})

def schedule_on_off(request,package_key):
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
            return_response = turning_on_off(schedule_type,package_key,is_on)
            if return_response["status"] == "success":
                message = "Watering "+ return_response["message"]
                return JsonResponse({'message':message})
            elif return_response["status"] == "error":
                message = "Failed to save watering schedule"
                return JsonResponse({'status':'error','message': message})

        else:
            schedule_type = "schedule_pesticide"
            return_response = turning_on_off(schedule_type,package_key, is_on)
            if return_response["status"] == "success":
                message = "Pestecide "+ return_response["message"]
                return JsonResponse({'message': message})
            elif return_response["status"] == "error":
                message = "Failed to save pestecide schedule"
                return JsonResponse({'status':'error', 'message': message})

    except Exception as e:
        print(e)
        return JsonResponse({'error': f'{e}'})


def schedule_reset(request,package_key):
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






