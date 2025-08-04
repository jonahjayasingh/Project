from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
    path("",index,name="home"),
    path("login/",userlogin,name="login"),
    path("register",userregister,name="register"),
    path("logout",userlogout,name="logout"),
    path("dashboard",dashboard,name="dashboard"),
    path("profile",profile,name="profile"),
    path("approve",approve,name="approve"),
    path("allstudents",allStudents,name="allstudents"),
]