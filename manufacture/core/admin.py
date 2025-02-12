from django.contrib import admin
from .models import *

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'path', 'method', 'timestamp', 'ip_address')
    search_fields = ('user', 'username', 'path', 'ip_address')
    list_filter = ('method', 'timestamp')

    # Custom form atau tampilan jika diperlukan

# Mendaftarkan model UserActivity di admin
admin.site.register(UserActivity, UserActivityAdmin)