from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path("login", userlogin, name='login'),
    path("register", register, name='register'),
    path("logout", userlogout, name='logout'),
    
]

company = [
    path("dashboard", companydashboard, name='dashboard'),
    path("jobdetails/<int:id>", jobdetails, name='jobdetails'),
    path("deletejob/<int:id>", deletejob, name='deletejob'),
    path("editjob/<int:id>", editjob, name='editjob'),
    path("active_status/<int:id>", active_status, name='active_status'),
    path("company_profile", company_profile, name='company_profile'),
]



urlpatterns += company