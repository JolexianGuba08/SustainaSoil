from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('location/', views.process_location, name='location_view'),
]
