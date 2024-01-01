import re
import string
import random
from django.db import models
import bcrypt
from homepage.firestore_db_modules.package_iot import add_package_iot


# Create your models here.
class Account(models.Model):
    acc_id = models.AutoField(primary_key=True)
    acc_email = models.EmailField(unique=True, verbose_name='Email')
    acc_password = models.TextField(verbose_name='password')
    ACC_TYPE = (
        (0, 'CUSTOMER'),
        (1, 'ADMIN')
    )
    acc_type = models.IntegerField(choices=ACC_TYPE, default=0, verbose_name='account type')
    acc_first_name = models.CharField(max_length=50, verbose_name='firstname')
    acc_last_name = models.CharField(max_length=50, verbose_name='lastname')
    ACC_STATUS = (
        (1, 'ACTIVE'),
        (2, 'DELETED'),
        (3, 'SUSPENDED'),
        (4, 'DEACTIVATED')
    )
    acc_status = models.IntegerField(choices=ACC_STATUS, default=1, verbose_name='account status')
    acc_profile_img = models.URLField(max_length=500, default='https://res.cloudinary.com/duku3q6xf/image/upload'
                                                              '/v1700856645/Aquamelya/default-user_a8bkjg.png',
                                      verbose_name='profile image')
    acc_background_img = models.URLField(max_length=500,
                                         default='https://res.cloudinary.com/duku3q6xf/image/upload/v1703269291/default_back_img_p4mkzo.png',
                                         verbose_name='profile image')
    acc_phone = models.CharField(max_length=11, default='', verbose_name='phone number')
    acc_date_added = models.DateTimeField(auto_now_add=True)
    acc_date_last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.acc_first_name + ' ' + self.acc_last_name

    def save(self, *args, **kwargs):
        if self.acc_password:
            hashed_password = bcrypt.hashpw(self.acc_password.encode('utf8'), bcrypt.gensalt())
            self.acc_password = hashed_password.decode('utf8')
        super(Account, self).save(*args, **kwargs)

    class Meta:
        db_table = 'account'
        verbose_name = 'account'
        verbose_name_plural = 'accounts'


class Plant_Preferences(models.Model):
    plant_pref_id = models.AutoField(primary_key=True)
    plant_min_temp = models.IntegerField(verbose_name='minimum temperature')
    plant_max_temp = models.IntegerField(verbose_name='maximum temperature')
    plant_min_moist_lvl = models.IntegerField(verbose_name='minimum moisture level')
    plant_max_moist_lvl = models.IntegerField(verbose_name='maximum moisture level')

    def __str__(self):
        return str(self.plant_pref_id)

    class Meta:
        db_table = 'plant_preferences'
        verbose_name = 'plant preference'
        verbose_name_plural = 'plant preferences'


class Plants(models.Model):
    plant_id = models.AutoField(primary_key=True)
    plant_name = models.CharField(max_length=50, verbose_name='plant name', unique=True)
    plant_species = models.CharField(max_length=100, verbose_name='plant species')
    plant_description = models.TextField(default='', verbose_name='plant description')
    plant_image = models.CharField(max_length=500, default='plant_images/default_plant_img.img',
                                  verbose_name='plant image')
    plant_date_added = models.DateTimeField(auto_now_add=True)
    plant_date_last_updated = models.DateTimeField(auto_now=True)
    plant_pref_id = models.ForeignKey(Plant_Preferences, on_delete=models.CASCADE, db_column='plant_pref_id',
                                      verbose_name='plant preference')
    PLANT_STATUS = (
        (1, 'ACTIVE'),
        (2, 'DELETED'),
    )
    plant_status = models.IntegerField(choices=PLANT_STATUS, default=1, verbose_name='plant status')

    def __str__(self):
        return self.plant_name

    class Meta:
        db_table = 'plants'
        verbose_name = 'plant'
        verbose_name_plural = 'plants'
def random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def default_starting_id(model, pk):
    last_id = model.objects.order_by(pk).first()

    if last_id:
        numeric_part = re.search(r'\d+$', getattr(last_id, pk))
        if numeric_part:
            return int(numeric_part.group()) + 1
    else:
        return 1001

def default_package_id():
    prefix = "HESUYAM"
    random_suffix = random_string(5)
    return f"{prefix}{random_suffix}_{default_starting_id(Packages, 'package_key')}"

class Packages(models.Model):
    package_key = models.CharField(primary_key=True,default = default_package_id)
    package_name = models.CharField(max_length=50, verbose_name='package name')
    package_description = models.TextField(default='', verbose_name='package description')
    package_slot = models.IntegerField(default=0, verbose_name='package slot')
    package_image = models.CharField(max_length=500, default='package_images/default_package.png',
                                    verbose_name='package image')
    package_date_added = models.DateTimeField(auto_now_add=True)
    package_date_last_updated = models.DateTimeField(auto_now=True)
    PACKAGE_STATUS = (
        (1, 'ACTIVE'),
        (2, 'DELETED'),
    )
    package_status = models.IntegerField(choices=PACKAGE_STATUS, default=1, verbose_name='package status')

    def __str__(self):
        return self.package_key

    def save(self, *args, **kwargs):
        iot_id = [random_string(8) for _ in range(5)]
        try:
            # Attempt to save the object
            super(Packages, self).save(*args, **kwargs)
            add_package_iot(self.package_key, *iot_id)

        except Exception as e:
            # Handle the exception if the object cannot be saved
            print(f"Error saving object: {e}")

    class Meta:
        db_table = 'packages'
        verbose_name = 'package'
        verbose_name_plural = 'packages'


class Account_Package(models.Model):
    acc_package_id = models.AutoField(primary_key=True)
    acc_package_name = models.CharField(max_length=50, verbose_name='account package name')
    date_added = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    package_key = models.ForeignKey(Packages, on_delete=models.CASCADE, db_column='package_key', verbose_name='package')
    user_id = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user_id', verbose_name='user')

    def __str__(self):
        return self.acc_package_name

    class Meta:
        db_table = 'account_package'
        verbose_name = 'account package'
        verbose_name_plural = 'account packages'


class Account_Plant_Preferences(models.Model):
    acc_plant_pref_id = models.AutoField(primary_key=True)
    acc_plant_min_temp = models.IntegerField(verbose_name='minimum temperature')
    acc_plant_max_temp = models.IntegerField(verbose_name='maximum temperature')
    acc_plant_min_moist_lvl = models.IntegerField(verbose_name='minimum moisture level')
    acc_plant_max_moist_lvl = models.IntegerField(verbose_name='maximum moisture level')

    def __str__(self):
        return str(self.acc_plant_pref_id)

    class Meta:
        db_table = 'acc_plant_preferences'
        verbose_name = 'acc_plant preference'
        verbose_name_plural = 'acc_plant preferences'

class Account_Plants(models.Model):
    acc_plant_id = models.AutoField(primary_key=True)
    plant_id = models.ForeignKey(Plants, on_delete=models.CASCADE, db_column='plant_id', verbose_name='plant')
    user_id = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user_id', verbose_name='user')
    package_key = models.ForeignKey(Packages, on_delete=models.CASCADE, db_column='package_key', verbose_name='package')
    date_added = models.DateTimeField(auto_now_add=True)
    acc_plant_pref_id = models.ForeignKey('Account_Plant_Preferences', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.acc_plant_id)

    class Meta:
        db_table = 'account_plants'
        verbose_name = 'account plant'
        verbose_name_plural = 'account plants'




class Schedules(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    schedule_water_key = models.CharField(max_length=200, default='', verbose_name='water schedule')
    schedule_pesticide_key = models.CharField(max_length=200, default='', verbose_name='pesticide schedule')

    def __str__(self):
        return str(self.schedule_id)

    class Meta:
        db_table = 'schedules'
        verbose_name = 'schedule'
        verbose_name_plural = 'schedules'
