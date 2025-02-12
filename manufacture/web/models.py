from django.db import models

# Create your models here.
class Testimonials(models.Model) :
    name = models.CharField(max_length=64)
    position = models.CharField(max_length=64)
    company_name = models.CharField(max_length=64)
    feedback = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    rating = models.IntegerField()

    class Meta :
        app_label = 'web'
        db_table = 'testimonials'
        managed = True
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'core'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'core'
        super().delete(*args, **kwargs)