from django.urls import path
from .views import *

app_name = "student"

urlpatterns = [
    path("",dashboard,name="student"),
    path("profile/",profile,name="profile"),
    path("notifications/<int:pk>/read/", mark_notification_read, name="mark_notification_read"),
    path("training/",training,name="training"),

]