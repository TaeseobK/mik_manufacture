from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    #Pages user_profile
    path('settings/user/', views.employee_list, name='employee_list'),

    #Detail user_profile
    path('settings/user/<int:employee_id>/', views.detail_user, name='user_detail'),
]