import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from master.models import *
from .models import *

def staff_required(user) :
    return user.is_staff

def admin_required(user) :
    return user.is_superuser

@login_required
@user_passes_test(admin_required, login_url='/login/')
def user_list(request) :
    search_query = request.GET.get('search', '')

    u = request.user
    profiles = Profile.objects.using('profile').get(user=int(u.pk))

    data = []

    user_list = User.objects.using('default').exclude(is_superuser=1)
    

    for d in user_list :
        profile = Profile.objects.using('profile').get(user=int(d.pk))

        if d.is_staff == True :
            status = "Staff"
        else :
            status = "Not Staff"

        
        if d.is_active == True :
            active = "Active"
        else :
            active = "Not Active"

        data.append({
            'user' : d,
            'status' : status,
            'active' : active,
            'profile' : profile
        }) 

    if search_query :
        data = [
            t for t in data
            if (
                search_query.lower() in str(t['user'].username).lower() or
                search_query.lower() in str(t['user'].email).lower() or
                search_query.lower() in str(t['status']).lower() or
                search_query.lower() in str(t['active']).lower() or
                search_query.lower() in str(t['profile'].company).lower()
            )
        ]

    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_profile/user_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_profile/user_list.html', {
        'title_1' : 'Settings',
        'title_2' : 'Users',
        'page_obj' : page_obj,
        'profile' : profiles
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def user_detail(request, u_id) :

    u = request.user
    profiles = Profile.objects.using('profile').get(user=int(u.pk))

    user = User.objects.using('default').get(id=int(u_id))

    if request.method == 'POST' :
        username = request.POST['username']
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['user-email']
        staff = request.POST.get('staff', 'off')
        activate = request.POST.get('active', 'off')

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if staff == 1 or staff == "1" :
            user.is_staff = True
        else :
            user.is_staff = False

        if activate == 1 or activate == "1" :
            user.is_active = True
        else :
            user.is_active = False

        if user.is_staff == True :
            new, created = Employee.objects.using('profile').get_or_create(
                user = user.pk
            )

            if not created :
                pass

        user.save()

        return redirect('user_profile:user_list')

    return render(request, 'detail_profile/user_detail.html', {
        'title_1' : 'Settings', 
        'title_2' : 'Detail User', 
        'user' : user,
        'profile' : profiles,
        'feature' : 'Cant Add'
    })