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
    path('profile_overview/', views.overview, name='overview'),
    path('profile_edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile_change_password/', views.change_password, name='change_password'),
]
