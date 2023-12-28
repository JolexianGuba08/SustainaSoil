from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('location/', views.process_location, name='location_view'),

    path('preloader/', views.preloader, name='preloader'),
    path('notifcation_web/', views.web_notif, name='web_notif'),
    path('notification_mobile/', views.mobile_notif, name='mobile_notif'),

    # Profile Urls
    path('profile/', views.profile, name='profile'),
    # path('profile_overview/', views.overview, name='overview'),
    # path('profile_edit_profile/', views.edit_profile, name='edit_profile'),
    # path('profile_change_password/', views.change_password, name='change_password'),

    # Greenery Urls
    path('greenery/', views.greenery, name='greenery'),
    path('presets/', views.presets, name='presets'),

    path('plant_profile/', views.plant_profile, name='plant_profile'),
    # Includes for Plant Profile Urls
    path('plant_profile_section/', views.plant_profile_section, name='plant_profile_section'),
    path('parameter_form/', views.parameter_form, name='parameter_form'),
    path('schedule_form/', views.schedule_form, name='schedule_form'),
]
