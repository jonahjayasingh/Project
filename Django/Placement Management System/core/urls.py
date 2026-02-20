from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.student_register, name='student_register'),
    path('company-register/', views.company_register, name='company_register'),
    path('login/', views.userlogin, name='userlogin'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    path('students/', views.students_list, name='students_list'),
    path('students/approve/<int:student_id>/', views.approve_student, name='approve_student'),
    path('companies/', views.companies_list, name='companies_list'),
    path('companies/approve/<int:company_id>/', views.approve_company, name='approve_company'),
    path('logout/', views.logout_view, name='logout'),
]


