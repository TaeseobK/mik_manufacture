from django.db import models
import json

"""
Wilayah Database 'Manufacturing'
"""


class BillofMaterials(models.Model) :
    bom = models.CharField(max_length=255, unique=True)
    product_id = models.IntegerField(default=0)
    component = models.JSONField()
    quantity = models.JSONField()
    warehouse = models.JSONField()
    bom_type = models.CharField(max_length=24, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'manufacturing'
        db_table = 'bill_of_materials'
        managed = True

    def __str__(self):
        return self.bom
    
    def save(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().delete(*args, **kwargs)

class ManufacturingOrders(models.Model) :
    mo_number = models.CharField(max_length=255, unique=True)
    product = models.IntegerField()
    bom_number = models.IntegerField(default=0)
    quantity = models.IntegerField()
    status = models.CharField(max_length=24, choices=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('in progress', 'In Progress'), ('done', 'Done')])
    responsible = models.CharField(max_length=255)
    product_component = models.JSONField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    warehouse = models.CharField(max_length=255, null=True, blank=True)
    stock_move_id = models.IntegerField()
    approved_by = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'manufacturing'
        db_table = 'manufacturing_orders'
        managed = True

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().delete(*args, **kwargs)

class WorkCenters(models.Model) :
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    efficiency = models.DecimalField(max_digits=5, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'manufacturing'
        db_table = 'work_centers'
        managed = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().delete(*args, **kwargs)
    
class WorkOrders(models.Model) :
    manufacturing_order = models.ForeignKey(ManufacturingOrders, on_delete=models.CASCADE)
    work_center = models.ForeignKey(WorkCenters, on_delete=models.CASCADE)
    sequence = models.IntegerField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('done', 'Done')])
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        app_label = 'manufacturing'
        db_table = 'work_orders'
        managed = True

    def __str__(self):
        return f'Work Order for {self.manufacturing_order.product} - {self.status}'

    def save(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) :
        kwargs['using'] = 'manufacturing'
        super().delete(*args, **kwargs)