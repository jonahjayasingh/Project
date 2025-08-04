from django.urls import path
from .views import *

app_name ="teacher"

urlpatterns = [
    path("",dashboard,name="teacher")
]