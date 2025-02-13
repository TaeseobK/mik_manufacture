from django.urls import path, include
from django.shortcuts import redirect, render
from . import views

app_name = "core"

urlpatterns = [
    #Pages Core
    path('', views.home, name="home"),

    #New Core
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),

    #Detail Core
    path('user/<int:id_user>/', views.profile, name='user_profile'),

    #API
    path('api/get-province/', views.get_province, name='get_province'),
    path('api/get-cities/<int:province_id>/', views.get_cities, name='get_cities'),
]