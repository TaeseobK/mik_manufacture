from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model) :
    user = models.IntegerField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    company = models.CharField(max_length=64, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    province = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    zip = models.CharField(max_length=64, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', default='mik.jpg', max_length=255)

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
    resume = models.TextField(null=True, blank=True)
    employer = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    work_information = models.TextField(null=True, blank=True)
    private_information = models.TextField(null=True, blank=True)
    settings = models.TextField(null=True, blank=True)
    work_permit = models.FileField(upload_to='user_upload_file/', null=True, blank=True, max_length=255)
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