import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.paginator import Paginator
from .models import *
from user_profile.models import *

def staff_required(user):
    return user.is_staff or user.is_superuser

def admin_required(user) :
    return user.groups.filter(name='Admin').exists()

def group_required(group_name) :
    def in_group(user) :
        return (user.is_authenticated and user.groups.filter(name=group_name).exists()) or user.is_superuser
    return user_passes_test(in_group)

@login_required
@user_passes_test(admin_required, login_url='/login/')
def general_settings(request) :

    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    return render(request, 'pages_master/general_settings.html', {
        'title_1' : 'Settings',
        'title_2' : 'General Settings',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def companies_list(request):
    search_query = request.GET.get('search', '')

    user = request.user
    profiles = Profile.objects.using('profile').get(user=int(user.pk))

    entities = Entity.objects.using('master').all()

    entity_data = []

    for entity in entities :
        branch_ids = entity.branch
        profile = CompanyProfile.objects.using('master').get(entity=entity)

        branch_data = []

        for branch_id in branch_ids :
            try:
                branch = Branch.objects.using('master').get(pk=branch_id)
                branch_profile = BranchProfile.objects.using('master').get(branch=branch)
            except (ValueError, Branch.DoesNotExist, BranchProfile.DoesNotExist):
                continue

            branch_data.append({
                'pk' : branch.pk,
                'branch_name' : branch.branch,
                'branch_address' : branch_profile.address
            })
        
        entity_data.append({
            'entity' : entity,
            'branches' : branch_data,
            'profile' : profile
        })

    if search_query :
        entity_data = [
            data for data in entity_data
            if (
                search_query.lower() in str(data['entity'].entity).lower() or
                any(search_query.lower() in branch['branch_name'].lower() for branch in data['branches']) or
                search_query.lower() in str(data['profile'].website).lower()
            )
        ]
    
    paginator = Paginator(entity_data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/companies_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/companies_list.html', {
        'title_1': 'Settings',
        'title_2': 'Companies',
        'page_obj': page_obj,
        'profile' : profiles
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_company(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        company_name = request.POST['name-company']
        street_1 = request.POST['street-1']
        street_2 = request.POST['street-2']
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip']
        country = request.POST['country']

        npwp = request.POST['npwp']
        company_phone = request.POST['phone']
        mobile = request.POST['mobile']
        email = request.POST['email']
        website = request.POST['website']

        branch_name = request.POST.getlist('branch-name[]')
        branch_phone = request.POST.getlist('branch-phone[]')
        branch_address = request.POST.getlist('branch-address[]')

        entity = Entity.objects.using('master').create(
            entity=company_name, 
            branch=""
        )

        company_profile = CompanyProfile.objects.using('master').create(
            entity = entity,
            street_1 = street_1,
            street_2 = street_2,
            city = city,
            state = state,
            zip_code = zip_code,
            country = country,
            npwp = npwp,
            phone = company_phone,
            mobile = mobile,
            email = email,
            website = website
        )
        company_profile.save()

        branches_list = []
        for name, branch_phone, address in zip(branch_name, branch_phone, branch_address) :
            branch = Branch.objects.using('master').create(branch=name)
            branch_profile = BranchProfile.objects.using('master').create(
                branch = branch,
                address = address,
                phone = branch_phone
            )
            branch_profile.save()
            branches_list.append(branch.id)

        entity.branch = branches_list
        entity.save()

        return redirect('master:companies_list')

    return render(request, 'master_new/new_company.html',{
        'title_1' : 'Settings',
        'title_2' : 'New Companies',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_company(request, company_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    entity = Entity.objects.using('master').get(id=company_id)
    company_profile = CompanyProfile.objects.using('master').get(entity=entity)

    branch_data = []

    if isinstance(entity.branch, str) :
        entity.branch = json.loads(entity.branch)
    
    for branch_id in entity.branch :
        branch = Branch.objects.using('master').get(id=branch_id)
        branch_profile = BranchProfile.objects.using('master').get(id=branch_id)

        branch_data.append({
            'branch' : branch,
            'branch_profile' : branch_profile
        })

    if request.method == 'POST' :
        entity.entity = request.POST.get('name-company', entity.entity)

        company_profile.entity = entity
        company_profile.street_1 = request.POST.get('street-1', company_profile.street_1)
        company_profile.street_2 = request.POST.get('street-2', company_profile.street_2)
        company_profile.city = request.POST.get('city', company_profile.city)
        company_profile.state = request.POST.get('state', company_profile.state)
        company_profile.zip_code = request.POST.get('zip', company_profile.zip_code)
        company_profile.country = request.POST.get('country', company_profile.country)
        company_profile.npwp = request.POST.get('npwp', company_profile.npwp)
        company_profile.phone = request.POST.get('phone', company_profile.phone)
        company_profile.mobile = request.POST.get('mobile', company_profile.mobile)
        company_profile.email = request.POST.get('email', company_profile.email)
        company_profile.website = request.POST.get('website', company_profile.website)          
        
        entity.save()
        company_profile.save()

        branch_name = request.POST.getlist('branch-name[]')
        branch_phone = request.POST.getlist('branch-phone[]')
        branch_address = request.POST.getlist('branch-address[]')

        branches_list = []

        for name, phone, address in zip(branch_name, branch_phone, branch_address) :
            branch = Branch.objects.using('master').filter(branch=name).first()

            if branch :
                branch_profile = BranchProfile.objects.using('master').get(branch=branch)
                branch_profile.address = address
                branch_profile.phone = phone
                branch_profile.save()

            else :
                branch = Branch.objects.using('master').create(branch=name)
                BranchProfile.objects.using('master').create(
                    branch=branch,
                    address=address,
                    phone=phone
                )

            branches_list.append(branch.id)

        entity.branch = json.dumps(branches_list)
        entity.save()

        return redirect('master:companies_list')
    
    return render(request, 'detail_master/detail_company.html', {
        'title_1' : 'Settings',
        'Title_2' : entity.entity,
        'feature' : 'Cant Add',
        'branches' : branch_data,
        'entity' : entity,
        'company_profile' : company_profile,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def job_position_list(request) :
    search_query = request.GET.get('search', '')

    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    job_position = JobPosition.objects.using('master').all()

    if search_query :
        job_position = [
            data for data in job_position
            if (
                search_query.lower() in str(data.name).lower()
            )
        ]

    paginator = Paginator(job_position, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/job_position_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/job_position_list.html', {
        'title_1' : 'Employees',
        'title_2' : 'Job Positions',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_job_position(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    
    if request.method == 'POST' :
        job_position = request.POST['job-name']

        JobPosition.objects.using('master').create(
            name=job_position
        )
        
        return redirect('master:job_position_list')
    
    return render(request, 'master_new/new_job_position.html', {
        'title_1' : 'Employees', 
        'title_2' : 'New Job Positions',
        'feature' : 'Cant Add',
        'profile' :profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_job_position(request, jb_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    job_position = JobPosition.objects.using('master').get(id=int(jb_id))

    if request.method == 'POST' :
        job_position.name = request.POST.get('job-name', job_position.name)
        
        job_position.save()

        return redirect('master:job_position_list')
    
    return render(request, 'detail_master/jb_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Job Position',
        'feature' : 'Cant Add',
        'job_position' : job_position,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def employment_types(request) :
    search_query = request.GET.get('search', '')

    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    data = EmploymentTypes.objects.using('master').all()

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d.name).lower()
            )
        ]
    
    paginator = Paginator(data, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/employment_types.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/employment_types.html', {
        'title_1' : 'Employees',
        'title_2' : 'Employment Types',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_employment_type(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        name = request.POST['type-name']
        
        EmploymentTypes.objects.using('master').create(
            name=name
        )

        return redirect('master:employment_types')

    return render(request, 'master_new/new_employment_type.html', {
        'title_1' : 'Employees',
        'title_2' : 'New Employment Type',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_employment_type(request, et_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    type = EmploymentTypes.objects.using('master').get(id=int(et_id))

    if request.method == 'POST' :
        type.name = request.POST.get('type-name', type.name)

        type.save()

        return redirect('master:employment_types')
    
    return render(request, 'detail_master/et_detail.html', {
        'title_1' : 'Employees', 
        'title_2' : 'Detail Employment Type',
        'feature' : 'Cant Add',
        'et' : type,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def skill_list(request) :
    search_query = request.GET.get('search', '')

    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    all_skills = Skills.objects.using('master').all()

    data_r = []

    for data in all_skills :
        data = data
        levels = json.loads(data.levels)
        skills = json.loads(data.skills)

        data_r.append({
            'data' : data,
            'levels' : levels,
            'skills' : skills
        })

    if search_query :
        data_r = [
            d for d in data_r
            if (
                search_query.lower() in str(d['data']).lower() or
                search_query.lower() in " ".join([str(t['level']) for t in d['levels']]).lower() or
                search_query.lower() in " ".join([str(t['progress']) for t in d['levels']]).lower() or
                search_query.lower() in " ".join([str(t['skill']) for t in d['skills']]).lower()
            )
        ]

    paginator = Paginator(data_r, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/skill_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/skill_list.html', {
        'title_1' : 'Employees',
        'title_2' : 'Skills',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_skills(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        skill_type = request.POST['type-name']
        skill_list = request.POST.getlist('skills[]')
        level_list = request.POST.getlist('levels[]')
        progress_list = request.POST.getlist('progress[]')

        skills = []

        for d in skill_list :
            skills.append({
                'skill' : d
            })
        
        levels = []

        for l, p in zip(level_list, progress_list) :
            levels.append({
                'level' : l,
                'progress' : int(p)
            })

        Skills.objects.using('master').create(
            skill_type=skill_type,
            skills=json.dumps(skills),
            levels=json.dumps(levels)
        )

        return redirect('master:skill_list')

    return render(request, 'master_new/new_skills.html', {
        'title_1' : 'Employee',
        'title_2' : 'New Skills',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_skills(request, skill_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    skill = Skills.objects.using('master').get(id=skill_id)
    skill.levels = json.loads(skill.levels)
    skill.skills = json.loads(skill.skills)

    return render(request, 'detail_master/skill_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Skill',
        'feature' : 'Cant Add',
        'data' : skill,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def departure_list(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    search_query = request.GET.get('search', '')

    all_departure = Departure.objects.using('master').all()

    if search_query :
        all_departure = [
            data for data in all_departure
            if (
                search_query.lower() in str(data.departure).lower()
            )
        ]

    paginator = Paginator(all_departure, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/departure_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/departure_list.html', {
        'title_1' : 'Employee',
        'title_2' : 'Departure Reason',
        'profile' : profile,
        'page_obj' : page_obj
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_departure(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    if request.method == 'POST' :
        name = request.POST['name']

        Departure.objects.using('master').create(
            departure=name
        )

        return redirect('master:departure_list')
    
    return render(request, 'master_new/new_departure.html', {
        'title_1' : 'Employee',
        'title_2' : 'New Departure Reason',
        'feature' : 'Cant Add',
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_departure(request, dp_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    departure = Departure.objects.using('master').get(id=int(dp_id))

    if request.method == 'POST' :
        departure.departure = request.POST['name']
        departure.save()
        
        return redirect('master:departure_list')

    return render(request, 'detail_master/detail_departure.html', {
        'title_1' : 'Employee',
        'title_2' : 'Detail Departure',
        'feature' : 'Cant Add',
        'data' : departure,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def work_locations(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    search_query = request.GET.get('search', '')

    work = WorkLocations.objects.using('master').all()

    if search_query :
        work = [
            data for data in work
            if (
                search_query.lower() in str(data.locations).lower() or
                search_query.lower() in str(data.company.entity).lower() or
                search_query.lower() in str(data.address).lower()
            )
        ]

    paginator = Paginator(work, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/work_locations.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/work_locations.html', {
        'title_1' : 'Employees',
        'title_2' : 'Work Locations',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_work_locations(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    company = Entity.objects.using('master').all()

    if request.method == 'POST' :
        location = request.POST['work-location']
        address = request.POST['work-address']
        company_id = request.POST['company']

        company_o = Entity.objects.using('master').get(id=int(company_id))

        WorkLocations.objects.using('master').create(
            locations=location,
            address=address,
            company=company_o
        )

        return redirect('master:work_locations')
    
    return render(request, 'master_new/new_work_location.html', {
        'title_1' : 'Employees',
        'title_2' : 'New Work Locations',
        'feature' : 'Cant Add',
        'company' : company,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_work_location(request, wk_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    wok = WorkLocations.objects.using('master').get(id=int(wk_id))

    company = Entity.objects.using('master').all()

    return render(request, 'detail_master/detail_wk.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Work Locations',
        'feature' : 'Cant Add',
        'data' : wok,
        'company' : company,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def department_list(request):
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))
    search_query = request.GET.get('search', '')

    data = []

    departments = Department.objects.using('master').all()

    for d in departments:
        manager = User.objects.using('default').get(id=int(d.manager))

        data.append({
            'department': d,
            'manager': manager.username
        })

    if search_query:
        data = [
            d for d in data
            if search_query.lower() in d['department'].department.lower() or
               search_query.lower() in d['manager'].lower()
        ]

    paginator = Paginator(data, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'pages_master/department.html', {
            'page_obj': page_obj
        })

    return render(request, 'pages_master/department.html', {
        'title_1': 'Employees',
        'title_2': 'Departments',
        'page_obj': page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def new_department(request) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    data = []

    company = Entity.objects.using('master').all()

    user = User.objects.filter(is_staff=1, is_active=1, is_superuser=0)

    department = Department.objects.using('master').filter(sub_department=0)

    data.append({
        'company' : company,
        'user' : user,
        'department' : department
    })

    if request.method == 'POST' :
        name = request.POST['department']
        manager = request.POST['manager']
        parent = request.POST['parent']
        company = request.POST['company']

        company_id = Entity.objects.using('master').get(id=int(company))
        manager_id = User.objects.using('default').get(id=int(manager))

        new = Department.objects.using('master').create(
            department=name,
            company=company_id,
            parent=parent if parent else None,
            manager=manager_id.pk,
            sub_department=0
        )

        if new.parent == None or new.parent == 0 :
            new.sub_department = 0

        else :
            new.sub_department = 1

        new.save()        

        return redirect('master:department_list')

    return render(request, 'master_new/new_department.html', {
        'title_1' : 'Employees',
        'title_2' : 'New Department',
        'feature' : 'Cant Add',
        'data' : data,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_department(request, d_id) :
    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    data = []

    company = Entity.objects.using('master').all()

    user = User.objects.filter(is_staff=1, is_active=1, is_superuser=0)

    department = Department.objects.using('master').filter(sub_department=0).exclude(id=int(d_id))

    data.append({
        'company' : company,
        'user' : user,
        'department' : department
    })

    department = Department.objects.using('master').get(id=int(d_id))

    if department.sub_department == 1 :
        department.parent = Department.objects.using('master').get(id=int(department.parent))
    else :
        department.parent = ''

    department.manager = User.objects.using('default').get(id=int(department.manager))

    if request.method == 'POST' :
        department_name = request.POST['department']
        manager = request.POST['manager']
        parent = request.POST['parent']
        company_d = request.POST['company']

        company_id = Entity.objects.using('master').get(id=int(company_d))
        manager_id = User.objects.using('default').get(id=int(manager))

        department.department = department_name
        department.manager = manager_id.pk
        department.parent = parent
        department.company = company_id

        if department.parent == '' or department.parent == None :
            department.sub_department = 0
        
        else :
            department.sub_department = 1

        department.save()

        return redirect('master:department_list')

    return render(request, 'detail_master/department_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Department',
        'feature' : 'Cant Add',
        'department' : department,
        'data' : data,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def employee_list(request) :
    search_query = request.GET.get('search', '')

    user = request.user
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    data = []

    employees = Employee.objects.using('profile').all()
    
    for d in employees :
        user = User.objects.using('default').get(id=int(d.user))

        if (
            not d.private_information == '' and
            not d.settings == '' and
            not d.resume == '' and
            not d.work_information == '' and
            not d.employer == '' and
            not d.work_permit == ''
        ) :
            status = "Up to Date"
        else :
            status = "Need Update"

        if user.is_superuser == 0 :

            data.append({
                'employee' : d,
                'user' : user,
                'status' : status
            })

    if search_query :
        data = [
            d for d in data
            if (
                search_query.lower() in str(d['user'].username) or
                search_query.lower() in str(d['status'])
            )
        ]

    paginator = Paginator(data, 9)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        return render(request, 'pages_master/employee_list.html', {
            'page_obj' : page_obj
        })

    return render(request, 'pages_master/employee_list.html', {
        'title_1' : 'Employees', 
        'title_2' : 'Employee List',
        'page_obj' : page_obj,
        'profile' : profile
    })

@login_required
@group_required('Employee')
@user_passes_test(staff_required, login_url='/login/')
def detail_employee(request, e_id) :
    user_n = request.user
    profiles = Profile.objects.using('profile').get(user=int(user_n.pk))


    data = []

    employee = Employee.objects.using('profile').get(id=int(e_id))
    user = User.objects.using('default').get(id=int(employee.user))
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    level = Level.objects.using('master').all()
    type_employment = EmploymentTypes.objects.using('master').all()
    position = JobPosition.objects.using('master').all()
    skills = Skills.objects.using('master').all()
    entity = CompanyProfile.objects.using('master').all()
    department = Department.objects.using('master').all()
    user_p = User.objects.using('default').filter(is_superuser=0, is_staff=1)

    distance = [
        'km', 'hm', 'dkm', 'm',
        'dm', 'cm', 'mm', 'in',
        'ft', 'yd', 'mi'
    ]

    gender = [
        'Male', 'Female'
    ]

    education = [
        'Graduate', 'Bachelor', 'Master', 'Doctor', 'Others'
    ]

    marital = [
        'Single', 'Married', 'Legal Cohabitant', 'Widower', 'Divorced'
    ]
    detail = Employee.objects.using('profile').get(user=int(user.pk))

    data.append({
        'employee' : employee,
        'user' : user,
        'level' : level,
        'type_employment' : type_employment,
        'position' : position,
        'skills' : skills,
        'entity' : entity,
        'department' : department,
        'profile' : profile,
        'user_p' : user_p,
        'distance' : distance,
        'gender' : gender,
        'education' : education,
        'marital' : marital
    })

    pp = {
        'employer' : json.loads(detail.employer) if detail.employer else None,
        'private_information' : json.loads(detail.private_information) if detail.private_information else None,
        'work_information' : json.loads(detail.work_information) if detail.work_information else None,
        'settings' : json.loads(detail.settings) if detail.settings else None
    }

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'post' :
            job_title = request.POST['job-title']
            phone_number = request.POST['phone-number']
            mobile_number = request.POST['mobile-number']
            tags = request.POST['tags']
            company = request.POST['company']

            department_p = request.POST['department']
            position_p = request.POST['position']
            manager = request.POST['manager']
            coach = request.POST['coach']

            #For The Resume

            #For the Work Information
            work_company = request.POST['work-company']

            #For the Employee Information
            #=================================================#
            employer = {
                'job_title' : job_title,
                'work_phone' : phone_number,
                'work_mobile' : mobile_number,
                'tags' : tags,
                'company' : company,
                'department' : department_p,
                'job_position' : position_p,
                'manager' : manager,
                'coach' : coach
            }


            #For the private information
            #=================================================#

            #PRIVATE CONTACT
            #----------------------------------#

            #ADDRESSSS===============
            street_1 = request.POST['street1']
            street_2 = request.POST['street2']
            state = request.POST['state']
            city = request.POST['city']
            zip = request.POST['zip']
            country = request.POST['country']

            #CONTACTT
            private_email = request.POST['private-email']
            private_phone = request.POST['private-phone']
            bank_number = request.POST['bank-number']
            bank_name = request.POST['bank-name']

            home_distance = request.POST['home-distance']
            long_measure = request.POST['distance']

            car_plate = request.POST['car-plate']


            #CITIZENSHIP
            #----------------------------------#

            nationality = request.POST['nationality']
            identification = request.POST['identification']
            ssn_no = request.POST['ssn']
            passport = request.POST['passport']
            gender_p = request.POST['gender']
            birth_date = request.POST['birthdate']
            birthplace = request.POST['birthplace']
            birthcountry = request.POST['birthcountry']


            #EMERGENCY
            #----------------------------------#
            contact_emergency = request.POST['contact-emergency']
            number_emergency = request.POST['phone-emergency']


            #EDUCATION
            #----------------------------------#
            certification = request.POST['certification']
            field_study = request.POST['field-study']
            school = request.POST['school']


            
            #FAMILY STATUS
            #----------------------------------#
            marital_status = request.POST['marital']
            dependent_children = request.POST['dependent-children']

            
            #WORK PERMIT
            #----------------------------------#
            no_visa = request.POST['visa']
            no_work_permit = request.POST['work-permit']
            exp_visa = request.POST['visa-expired']
            exp_work_permit = request.POST['work-permit-expiry']

            files = request.FILES.get('work-permit-file')

            file_name = None

            if files :
                file_name = f'work_permit/{files.name}'
                file_name = default_storage.save(file_name, files)
                file_url = default_storage.url(file_name)


            #For the Settings
            #=================================================#
            
            #Status
            employee_type = request.POST['employee-status']

            #Pay Rate
            pay_rate = request.POST['pay-rate']


            #WORK INFORMATION DATA
            #=================================#

            company_profile = CompanyProfile.objects.using('master').get(entity=int(work_company))

            work_information = {
                'company' : int(work_company),
                'work_address' : {
                    'street_1' : company_profile.street_1.upper(),
                    'street_2' : company_profile.street_2.upper(),
                    'city' : company_profile.city.upper(),
                    'state' : company_profile.state.upper(),
                    'zip' : company_profile.zip_code,
                    'country' : company_profile.country
                }
            }


            #PRIVATE INFORMATION DATA
            #=================================#
            if birth_date :
                date_of_birth = datetime.strptime(birth_date,'%Y/%m/%d')
                birthdateobj = date_of_birth.strftime('%Y-%m-%d')

            else :
                birthdateobj = ""

            if exp_visa :
                visa_exp = datetime.strptime(exp_visa, '%Y/%m/%d')
                visa_exp_date = visa_exp.strftime('%Y-%m-%d')
            
            else :
                visa_exp_date = ""

            if exp_work_permit :
                work_permit_exp = datetime.strptime(exp_work_permit, '%Y/%m/%d')
                work_permit_exp_date = work_permit_exp.strftime('%Y-%m-%d')

            else :
                work_permit_exp_date = ""

            private_information = {
                'private_contact' : {
                    'private_address' : {
                        'street_1' : street_1,
                        'street_2' : street_2,
                        'state' : state,
                        'city' : city,
                        'zip' : zip,
                        'country' : country
                    },
                    'private_email' : private_email,
                    'private_phone' : private_phone,
                    'bank_account' : {
                        'number' : bank_number,
                        'name' : bank_name
                    },
                    'home_distance' : {
                        'distance' : home_distance,
                        'measure' : long_measure
                    },
                    'private_car_plate' : car_plate
                },
                'citizenship' : {
                    'nationality' : nationality,
                    'identification_number' : identification,
                    'ssn_no' : ssn_no,
                    'passport_no' : passport,
                    'gender' : gender_p,
                    'date_of_birth' : birthdateobj,
                    'birthplace' : birthplace,
                    'birthcountry' : birthcountry
                },
                'emergency_contact' : {
                    'contact_name' : contact_emergency,
                    'contact_number' : number_emergency
                },
                'education' : {
                    'certification' : certification,
                    'field_of_study' : field_study,
                    'school' : school
                },
                'family_status' : {
                    'marital_status' : marital_status,
                    'dependent_children' : dependent_children,
                },
                'work_permit' : {
                    'visa_no' : no_visa,
                    'work_permit_no' : no_work_permit,
                    'visa_exp' : visa_exp_date,
                    'work_permit_exp' : work_permit_exp_date
                }
            }


            #SETTINGS
            #=================================#
            setting = {
                'status' : employee_type,
                'pay_rate' : pay_rate
            }

            employee.private_information = json.dumps(private_information)
            employee.work_information = json.dumps(work_information)
            employee.settings = json.dumps(setting)
            employee.employer = json.dumps(employer)

            employee.save()

            return redirect('master:employee_list')

    return render(request, 'detail_master/detail_employee.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Employee',
        'feature' : 'Cant Add',
        'data' : data,
        'pp' : pp,
        'profile' : profiles
    })