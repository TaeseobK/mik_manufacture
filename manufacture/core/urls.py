from django.urls import path, include
from django.shortcuts import redirect, render
from . import views

app_name = "core"

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
]