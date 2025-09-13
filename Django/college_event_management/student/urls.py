from django.urls import path
from . import views

app_name ="student"

urlpatterns = [
    path('',views.index,name="student"),
    path("mcq_exam",views.mcq_exam,name="mcq_exam"),

    
]
