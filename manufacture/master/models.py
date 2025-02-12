from django.db import models
from datetime import datetime

class Skills(models.Model) :
    skill_type = models.CharField(max_length=64)
    skills = models.TextField()
    levels = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'skills'
        managed = True

    def __str__(self) :
        return self.skill_type
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class JobPosition(models.Model) :
    name = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'job_position'
        managed = True

    def __str__(self) :
        return self.name
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class EmploymentTypes(models.Model) :
    name = models.CharField(max_length=64)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'employment_types'
        managed = True

    def __str__(self) :
        return self.name
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Level(models.Model) :
    level = models.CharField(max_length=64)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'level'
        managed = True

    def __str__(self) :
        return self.level
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Departure(models.Model) :
    departure = models.CharField(max_length=64)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'departure'
        managed = True

    def __str__(self) :
        return self.departure
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Branch(models.Model) :
    branch = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'branch'
        managed = True

    def __str__(self) :
        return self.branch
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Entity(models.Model) :
    entity = models.CharField(max_length=64)
    branch = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'entity'
        managed = True

    def __str__(self) :
        return self.entity
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class WorkLocations(models.Model) :
    locations = models.CharField(max_length=255)
    company = models.ForeignKey(Entity, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'work_locations'
        managed = True

    def __str__(self) :
        return self.locations
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class CompanyProfile(models.Model) :
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    street_1 = models.TextField()
    street_2 = models.TextField()
    city = models.TextField()
    state = models.TextField()
    zip_code = models.IntegerField()
    country = models.TextField()
    npwp = models.TextField()
    phone = models.TextField()
    mobile = models.TextField()
    email = models.EmailField()
    website = models.URLField()

    class Meta :
        app_label = 'master'
        db_table = 'company_profile'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class BranchProfile(models.Model) :
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    address = models.TextField()
    phone = models.TextField(null=True, blank=True)

    class Meta :
        app_label = 'master'
        db_table = 'branch_profile'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

shipping_choices = [
    ('internal', 'Internal Service'),
    ('external', 'External Services'),
]

class ShippingService(models.Model) :
    name = models.CharField(max_length=64)
    service_type = models.CharField(max_length=24, choices=shipping_choices, default='internal')
    website = models.URLField(blank=True, null=True)
    contact_admin = models.CharField(max_length=24, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'master'
        db_table = 'shipping_service'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)

class Department(models.Model) :
    department = models.CharField(max_length=255)
    company = models.ForeignKey(Entity, on_delete=models.CASCADE)
    parent = models.IntegerField(null=True, blank=True)
    manager = models.IntegerField(null=True, blank=True)
    sub_department = models.BooleanField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.department

    class Meta :
        app_label = 'master'
        db_table = 'department'
        managed = True

    def __str__(self) :
        return self.department
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'master'
        super().delete(*args, **kwargs)