from django.urls import path
from .views import *

app_name ="teacher"

urlpatterns = [
    path("",dashboard,name="teacher"),
    path("profile/",profile,name="profile"),
    path("approvestudents/",approvestudents,name="approvestudents"),
    path("approve/<int:id>",approve,name="approve"),
    path("reject/<int:id>",reject,name="reject"),
    path("resume",resume,name="resume"),
    path("recjec_resume",reject_resume,name="reject_resume"),
    path("allstudent",all_student,name="allstudent"),
    path("group_notification",group_notification,name="group_notification"),
]