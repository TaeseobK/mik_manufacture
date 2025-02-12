from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model) :
    user = models.IntegerField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    company = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images', default='mik.jpg')

    class Meta :
        app_label = 'user_profile'
        db_table = 'profile'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'profile'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'profile'
        super().delete(*args, **kwargs)

class Employee(models.Model) :
    user = models.IntegerField()
    department = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    type_employment = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    skills = models.IntegerField(default=0)
    entity = models.IntegerField(default=0)
    department = models.IntegerField(default=0)
    address = models.TextField(null=True, blank=True)
    join_date = models.DateField(null=True, blank=True)
    leave_date = models.DateField(null=True, blank=True)
    code = models.CharField(max_length=64)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'user_profile'
        db_table = 'employee'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'profile'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'profile'
        super().delete(*args, **kwargs)