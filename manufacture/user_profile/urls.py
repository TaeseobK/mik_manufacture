from django.urls import path
from . import views

app_name = 'user_profile'

urlpatterns = [
    #Pages user_profile
    path('settings/user/', views.user_list, name='user_list'),

    #Detail user_profile
    path('settings/user/<int:u_id>/', views.user_detail, name='user_detail'),
]