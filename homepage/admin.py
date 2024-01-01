from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Plant_Preferences)
admin.site.register(Account_Plant_Preferences)
admin.site.register(Plants)
admin.site.register(Packages)
admin.site.register(Account_Package)
admin.site.register(Account_Plants)
