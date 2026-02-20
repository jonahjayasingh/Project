from django.urls import path
from . import views

app_name ="student"

urlpatterns = [
    path('',views.index,name="student"),
    path("register_event",views.student_register,name="register_event"),
    path("cancel_register",views.cancel_register,name="cancel_register"),
    path("mcq_exam/<int:id>/",views.mcq_exam,name="mcq_exam"),
    path("profile",views.profile,name="profile"),
    path("my_certificates",views.my_certificates,name="my_certificates"),
    path("handle_sgpa",views.handle_sgpa,name="handle_sgpa"),


    
]
