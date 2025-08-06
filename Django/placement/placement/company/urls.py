from django.urls import path
from .views import *

app_name = "company"

urlpatterns = [
    path("",dashboard,name="company"),
    path("profile",profile,name="profile"),    
]