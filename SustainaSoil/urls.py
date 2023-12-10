from django.contrib import admin
from django.urls import path, include
from loginpage import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('login/', include('loginpage.urls')),
    path('signup/', views.signup_page, name='signup_page'),
]
