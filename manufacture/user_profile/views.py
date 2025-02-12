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
def employee_list(request) :

    data = []

    employees = Employee.objects.using('profile').all()
    
    for e in employees :
        user = User.objects.using('default').get(id=int(e.user))
        if not user.is_superuser == 1 :
            if not e.entity == 0 :
                e.entity = Entity.objects.using('master').get(id=int(e.entity))
            
            else :
                e.entity = e.entity

            if (
                not e.department == 0 and
                not e.level == 0 and
                not e.type_employment == 0 and
                not e.position == 0 and
                not e.entity == 0 and
                not e.department == 0
            ) :
                status = "Active"
            
            else :
                status = "Not Active"

            data.append({
                'employee' : e,
                'user' : user,
                'status' : status
            })

    return render(request, 'pages_profile/user_list.html', {
        'title_1' : 'Settings',
        'title_2' : 'Users',
        'data' : data
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_user(request, employee_id) :
    
    data = []

    e = Employee.objects.using('profile').get(id=int(employee_id))
    user = User.objects.using('default').get(id=int(e.user))
    level = Level.objects.using('master').all()
    type_employment = EmploymentTypes.objects.using('master').all()
    position = JobPosition.objects.using('master').all()
    skills = Skills.objects.using('master').all()
    entity = Entity.objects.using('master').all()
    department = Department.objects.using('master').all()

    data.append({
        'employee' : e,
        'user' : user,
        'level' : level,
        'type' : type_employment,
        'position' : position,
        'skills' : skills,
        'entity' : entity,
        'department' : department
    })

    return render(request, 'detail_profile/user_detail.html', {
        'title_1' : 'Settings',
        'title_2' : 'Detail User',
        'feature' : 'Cant Add',
        'data' : data
    })