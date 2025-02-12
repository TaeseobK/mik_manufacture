from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def staff_required(user) :
    return user.is_staff

# @login_required
# @user_passes_test(staff_required, login_url='/login/')
# def edit_web(request) :
