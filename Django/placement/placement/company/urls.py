from django.urls import path
from .views import *

app_name = "company"

urlpatterns = [
    path("",dashboard,name="company"),
    path("profile",profile,name="profile"),    
    path("jobs",jobs,name="jobs"),
    path("deletejob/<int:id>",deletejob,name="deletejob"),


]