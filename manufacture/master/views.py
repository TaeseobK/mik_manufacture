import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from .models import *
from user_profile.models import *

def staff_required(user):
    return user.is_staff

def admin_required(user) :
    return user.is_superuser

@login_required
@user_passes_test(staff_required, login_url='/login/')
def general_settings(request) :
    return render(request, 'pages_master/general_settings.html', {
        'title_1' : 'Settings',
        'title_2' : 'General Settings',
        'feature' : 'Cant Add'
    })

@login_required
@user_passes_test(staff_required, login_url='/login/')
def companies_list(request):

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

    return render(request, 'pages_master/companies_list.html', {
        'title_1': 'Settings',
        'title_2': 'Companies',
        'entities': entity_data
    })

@login_required
@user_passes_test(staff_required, login_url='/login/')
def new_company(request) :
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
    })

@login_required
@user_passes_test(staff_required, login_url='/login/')
def detail_company(request, company_id) :
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
        'company_profile' : company_profile
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def employee_list(request) :
    return render(request, 'pages_master/employee_list.html', {
        'title_1' : 'Employees',
        'title_2' : 'Employees'
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def job_position_list(request) :

    job_position = JobPosition.objects.using('master').all()

    return render(request, 'pages_master/job_position_list.html', {
        'title_1' : 'Employees',
        'title_2' : 'Job Positions',
        'job_position' : job_position
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_job_position(request) :
    
    if request.method == 'POST' :
        job_position = request.POST['job-name']

        JobPosition.objects.using('master').create(
            name=job_position
        )
        
        return redirect('master:job_position_list')
    
    return render(request, 'master_new/new_job_position.html', {
        'title_1' : 'Employees', 
        'title_2' : 'New Job Positions',
        'feature' : 'Cant Add'
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_job_position(request, jb_id) :

    job_position = JobPosition.objects.using('master').get(id=int(jb_id))

    if request.method == 'POST' :
        job_position.name = request.POST.get('job-name', job_position.name)
        
        job_position.save()

        return redirect('master:job_position_list')
    
    return render(request, 'detail_master/jb_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Job Position',
        'feature' : 'Cant Add',
        'job_position' : job_position
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def employment_types(request) :

    data = EmploymentTypes.objects.using('master').all()

    return render(request, 'pages_master/employment_types.html', {
        'title_1' : 'Employees',
        'title_2' : 'Employment Types',
        'data' : data
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_employment_type(request) :

    if request.method == 'POST' :
        name = request.POST['type-name']
        
        EmploymentTypes.objects.using('master').create(
            name=name
        )

        return redirect('master:employment_types')

    return render(request, 'master_new/new_employment_type.html', {
        'title_1' : 'Employees',
        'title_2' : 'New Employment Type',
        'feature' : 'Cant Add'
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_employment_type(request, et_id) :

    type = EmploymentTypes.objects.using('master').get(id=int(et_id))

    if request.method == 'POST' :
        type.name = request.POST.get('type-name', type.name)

        type.save()

        return redirect('master:employment_types')
    
    return render(request, 'detail_master/et_detail.html', {
        'title_1' : 'Employees', 
        'title_2' : 'Detail Employment Type',
        'feature' : 'Cant Add',
        'et' : type
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def skill_list(request) :

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

    return render(request, 'pages_master/skill_list.html', {
        'title_1' : 'Employees',
        'title_2' : 'Skills',
        'page_obj' : data_r
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_skills(request) :

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
        'feature' : 'Cant Add'
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_skills(request, skill_id) :
    skill = Skills.objects.using('master').get(id=skill_id)
    skill.levels = json.loads(skill.levels)
    skill.skills = json.loads(skill.skills)

    return render(request, 'detail_master/skill_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Skill',
        'feature' : 'Cant Add',
        'data' : skill
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def departure_list(request) :

    all_departure = Departure.objects.using('master').all()

    return render(request, 'pages_master/departure_list.html', {
        'title_1' : 'Employee',
        'title_2' : 'Departure Reason',
        'data' : all_departure
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_departure(request) :

    if request.method == 'POST' :
        name = request.POST['name']

        Departure.objects.using('master').create(
            departure=name
        )

        return redirect('master:departure_list')
    
    return render(request, 'master_new/new_departure.html', {
        'title_1' : 'Employee',
        'title_2' : 'New Departure Reason',
        'feature' : 'Cant Add'
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_departure(request, dp_id) :

    departure = Departure.objects.using('master').get(id=int(dp_id))

    return render(request, 'detail_master/detail_departure.html', {
        'title_1' : 'Employee',
        'title_2' : 'Detail Departure',
        'feature' : 'Cant Add',
        'data' : departure
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def work_locations(request) :
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
        'page_obj' : page_obj
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_work_locations(request) :

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
        'company' : company
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_work_location(request, wk_id) :

    wok = WorkLocations.objects.using('master').get(id=int(wk_id))

    company = Entity.objects.using('master').all()

    return render(request, 'detail_master/detail_wk.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Work Locations',
        'feature' : 'Cant Add',
        'data' : wok,
        'company' : company
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def department_list(request):
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
        'page_obj': page_obj
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def new_department(request) :

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

        if new.parent == 'None' or new.parent == '' :
            new.sub_department = 0
        else :
            new.sub_department = 1

        new.save()        

        return redirect('master:department_list')

    return render(request, 'master_new/new_department.html', {
        'title_1' : 'Employees',
        'title_2' : 'New Department',
        'feature' : 'Cant Add',
        'data' : data
    })

@login_required
@user_passes_test(admin_required, login_url='/login/')
def detail_department(request, d_id) :

    data = []

    company = Entity.objects.using('master').all()

    user = User.objects.filter(is_staff=1, is_active=1, is_superuser=0)

    department = Department.objects.using('master').filter(sub_department=0)

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

    return render(request, 'detail_master/department_detail.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Department',
        'feature' : 'Cant Add',
        'department' : department,
        'data' : data
    })

@login_required
@user_passes_test(staff_required, login_url='/login/')
def employee_list(request) :

    data = []

    employees = Employee.objects.using('profile').all()
    
    for d in employees :
        user = User.objects.using('default').get(id=int(d.user))

        if user.is_superuser == 0 :

            if not d.level == 0 :
                level = Level.objects.using('master').get(id=int(d.level))
            
            else :
                level = ""

            if not d.department == 0 :
                department = Department.objects.using('master').get(id=int(d.department))
            
            else :
                department = ""

            if not d.entity == 0 :
                entity = Entity.objects.using('master').get(id=int(d.entity))

            else :
                entity = ""

            if not d.position == 0 :
                position = JobPosition.objects.using('master').get(id=int(d.position))
            
            else :
                position = ""

            if (
                d.level == 0 or
                d.department == 0 or
                d.entity == 0 or
                d.position == 0 or
                d.position == 0
            ) :
                status = "Not Activated"
            
            else :
                status = "Active"

            data.append({
                'employee' : d,
                'user' : user,
                'level' : level,
                'department' : department,
                'entity' : entity,
                'position' : position,
                'status' : status
            })

    return render(request, 'pages_master/employee_list.html', {
        'title_1' : 'Employees', 
        'title_2' : 'Employee List',
        'data' : data
    })

@login_required
@user_passes_test(staff_required, login_url='/login/')
def detail_employee(request, e_id) :

    data = []

    employee = Employee.objects.using('profile').get(id=int(e_id))
    user = User.objects.using('default').get(id=int(employee.user))
    profile = Profile.objects.using('profile').get(user=int(user.pk))

    level = Level.objects.using('master').all()
    type_employment = EmploymentTypes.objects.using('master').all()
    position = JobPosition.objects.using('master').all()
    skills = Skills.objects.using('master').all()
    entity = Entity.objects.using('master').all()
    department = Department.objects.using('master').all()

    data.append({
        'employee' : employee,
        'user' : user,
        'level' : level,
        'type_employment' : type_employment,
        'position' : position,
        'skills' : skills,
        'entity' : entity,
        'department' : department,
        'profile' : profile
    })

    for d in data :
        print(d['profile'])

    return render(request, 'detail_master/detail_employee.html', {
        'title_1' : 'Employees',
        'title_2' : 'Detail Employee',
        'feature' : 'Cant Add',
        'data' : data
    })