from django.db import models
import bcrypt


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
    # acc_background_img = models.URLField(max_length=500, default='https://res.cloudinary.com/duku3q6xf/image/upload'
    #                                                              '/v1700856645/Aquamelya/default-user_a8bkjg.png',
    #                                      verbose_name='profile image')
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
    plant_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='plant price')
    plant_image = models.URLField(max_length=500, default='https://res.cloudinary.com/duku3q6xf/image/upload'
                                                          '/v1702344674/Aquamelya/default-plant-image_a9blla.png',
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


class Packages(models.Model):
    package_key = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=50, unique=True, verbose_name='package name')
    package_description = models.TextField(default='', verbose_name='package description')
    package_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='package price')
    package_slot = models.IntegerField(default=0, verbose_name='package slot')
    package_image = models.URLField(max_length=500, default='https://res.cloudinary.com/duku3q6xf/image/upload'
                                                            '/v1702344674/Aquamelya/default-package-image_a9blla.png',
                                    verbose_name='package image')
    package_date_added = models.DateTimeField(auto_now_add=True)
    package_date_last_updated = models.DateTimeField(auto_now=True)
    PACKAGE_STATUS = (
        (1, 'ACTIVE'),
        (2, 'DELETED'),
    )
    package_status = models.IntegerField(choices=PACKAGE_STATUS, default=1, verbose_name='package status')

    def __str__(self):
        return self.package_name

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


class Account_Plants(models.Model):
    acc_plant_id = models.AutoField(primary_key=True)
    plant_id = models.ForeignKey(Plants, on_delete=models.CASCADE, db_column='plant_id', verbose_name='plant')
    user_id = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='user_id', verbose_name='user')
    package_key = models.ForeignKey(Packages, on_delete=models.CASCADE, db_column='package_key', verbose_name='package')
    date_added = models.DateTimeField(auto_now_add=True)

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
