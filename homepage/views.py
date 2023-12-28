import json

from django.http import JsonResponse
from django.shortcuts import render, redirect

from homepage.forms import EditProfileForm
from homepage.user_context.context_processor import user_context
import homepage.firestore_db_modules.cloud_storage as cloud_storage


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
def greenery(request):
    return render(request, 'greenery_page/user-greenery.html')


def presets(request):
    return render(request, 'greenery_page/user-presets.html')


def plant_profile(request):
    return render(request, 'greenery_page/plant-profile.html')


def plant_profile_section(request):
    return render(request, 'greenery_page/plant-profile.html')


# Includes Plant Profile Views
def parameter_form(request):
    return render(request, 'greenery_page/include_plant_profile/parameter_form.html')


def schedule_form(request):
    return render(request, 'greenery_page/include_plant_profile/schedule_form.html')
