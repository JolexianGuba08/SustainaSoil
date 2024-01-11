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
    path('get_profile/', views.get_profile_value, name='get_profile_value'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('check_old_password/', views.check_password, name='check_password'),
    path('change_password/', views.change_password, name='change_password'),
    # path('profile_overview/', views.overview, name='overview'),
    # path('profile_edit_profile/', views.edit_profile, name='edit_profile'),
    # path('profile_change_password/', views.change_password, name='change_password'),

    # Greenery Urls
    path('greenery/', views.greenery, name='greenery'),
    path('presets/<str:package_key>', views.presets, name='presets'),
    path('add_plant/<str:package_key>', views.add_plant, name='add_plant'),
    path('plant_profile/<str:package_key>/<int:plant_id>', views.plant_profile, name='plant_profile'),
    path('take_care_plant/', views.take_care_plant, name='take_care_plant'),
    path('check_package_id/', views.check_package_id, name='check_package_id'),
    path('add_package/', views.add_package, name='add_package'),
    path('get_location/', views.get_location, name='get_location'),
    path('update_acc_preference/', views.save_acc_preferences, name='update_acc_preferences'),
    path('set_default_values/', views.set_default_values, name='set_default_values'),
    path('water_scheduling/<str:package_key>/', views.water_scheduling, name='water_scheduling'),
    path('schedule_on_off/<str:package_key>/', views.schedule_on_off, name='schedule_on_off'),
    path('schedule_reset/<str:package_key>/', views.schedule_reset, name='schedule_reset'),

    # Forums Urls
    path('forums/', views.forums, name='forums'),
    path('view_comments/', views.view_comment_forums, name='view_comments'),
    path('create-forum-post/', views.create_forum_post, name='create_forum_post')
]
