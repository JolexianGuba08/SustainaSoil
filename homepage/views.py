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

# Other imports...
from homepage.forms import EditProfileForm, ChangePasswordForm
from homepage.models import Packages, Account_Package, Account, Account_Plants, Plants, Account_Plant_Preferences
from homepage.user_context.context_processor import user_context
import homepage.firestore_db_modules.cloud_storage as cloud_storage
import homepage.firestore_db_modules.account_greenery as account_greenery


# Create your views here.
def homepage(request):
    if 'session_email' not in request.session and 'session_user_id' not in request.session and 'session_user_type' not in request.session:
        return redirect('login_page')
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
    try:
        account_package = Account_Package.objects.get(user_id=request.session.get('session_user_id'))
        if account_package:
            return render(request, 'greenery_page/user-greenery.html', {'account_package': account_package})
    except Account_Package.DoesNotExist:
        return render(request, 'greenery_page/user-greenery.html')


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
        try:
            package_key = Packages.objects.get(package_key=package_id)
            email = Account.objects.get(acc_email=user_email)
            if package_key:
                package_id_exist = Account_Package.objects.filter(package_key=package_id).first()
                if not package_id_exist:
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

        account_plants = Account_Plants.objects.get(user_id=request.session.get('session_user_id'))
        if account_plants:
            plant_img = cloud_storage.get_file_url_from_firebase(account_plants.plant_id.plant_image)
            print(plant_img)

    except Account_Plants.DoesNotExist:
        # Handle the case where the object is not found
        account_plant = None

    return render(request, 'greenery_page/add-plant.html', {
        'account_plants': account_plant,  # Use account_plant instead of account_plants
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


def plant_profile(request, package_key, plant_id):
    user_id = request.session.get('session_user_id')
    print(user_id, plant_id, package_key)

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
    return render(
        request,
        'greenery_page/plant-profile.html',
        {
            'plants': plants,
            'package_key': package_key,
            'take_cared': take_cared,
            'acc_plant': acc_plant,
            'plant_image_url': plant_image_url
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
            return JsonResponse({'message': 'User preferences updated successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'{e}'})


def plant_profile_section(request):
    return render(request, 'greenery_page/plant-profile.html')


# Includes Plant Profile Views
def parameter_form(request):
    return render(request, 'greenery_page/include_plant_profile/parameter_form.html')


def schedule_form(request):
    return render(request, 'greenery_page/include_plant_profile/schedule_form.html')


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
