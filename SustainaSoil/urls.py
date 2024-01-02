from django.contrib import admin
from django.urls import path, include
from loginpage import views
from homepage import urls as homepage_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(homepage_urls)),
    path('login/', include('loginpage.urls')),
    path('logout/', views.logout_page, name='logout_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('signup/otp/', views.otp_verification, name='otp_verification'),
    path('signup/otp/resend', views.resend_otp, name='otp_resend')
]
