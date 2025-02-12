from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    #Pages List
    path('settings/', views.general_settings, name='general_settings'),
    path('companies/', views.companies_list, name='companies_list'),
    path('employee/', views.employee_list, name='employee_list'),
    path('employee/job-position-list/', views.job_position_list, name='job_position_list'),
    path('employee/employment-types/', views.employment_types, name='employment_types'),
    path('employee/skill-list/', views.skill_list, name='skill_list'),
    path('employee/departure-list/', views.departure_list, name='departure_list'),
    path('employee/work-locations/', views.work_locations, name='work_locations'),
    path('employee/departments/', views.department_list, name='department_list'),

    #Pages New
    path('companies/new/', views.new_company, name='new_company'),
    path('employee/job-position/new/', views.new_job_position, name='new_job_position'),
    path('employee/employment-type/new/', views.new_employment_type, name='new_employment_type'),
    path('employee/skills/new/', views.new_skills, name='new_skills'),
    path('employee/departure/new/', views.new_departure, name='new_departure'),
    path('employee/work-locations/new/', views.new_work_locations, name='new_wl'),
    path('employee/departments/new/', views.new_department, name='new_department'),

    #Pages Detail
    path('companies/<int:company_id>/', views.detail_company, name='detail_company'),
    path('employee/job-position/<int:jb_id>/', views.detail_job_position, name='detail_jb'),
    path('employee/employment-type/<int:et_id>/', views.detail_employment_type, name='detail_et'),
    path('employee/skill/<int:skill_id>/', views.detail_skills, name='detail_skill'),
    path('employee/departure/<int:dp_id>/', views.detail_departure, name='detail_departure'),
    path('employee/work-location/<int:wk_id>/', views.detail_work_location, name='detail_wl'),
    path('employee/department/<int:d_id>/', views.detail_department, name='detail_d'),
    path('employee/employee/<int:e_id>/', views.detail_employee, name='detail_e'),
]