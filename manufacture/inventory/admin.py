from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_filter = ('destination', 'operation_type')
    list_display = ('id', 'destination', 'code', 'notes', 'operation_type')
    search_fields = ('id', 'code')

@admin.register(InternalTransfer)
class InternalransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'status', 'shipping_service', 'url_tracking')
    list_filter = ('status', 'id')
    search_fields = ('id', 'status')