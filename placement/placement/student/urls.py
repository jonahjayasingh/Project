from django.urls import path
from .views import *

app_name = "student"

urlpatterns = [
    path("",dashboard,name="student"),
    path("profile/",profile,name="profile"),
]