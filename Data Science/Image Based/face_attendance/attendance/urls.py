from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_student/', views.register_student, name='register_student'),
    path('enroll/', views.enroll_step1, name='enroll_step1'),
    path('save_enrollment/', views.save_enrollment, name='save_enrollment'),
    path('start_recognition/', views.start_recognition, name='start_recognition'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('data/', views.data, name='data'),
    path('my_attendance/', views.my_attendance, name='my_attendance'),
    path('studentdata/', views.student_data, name='student_data'),
    path('delete_student/<int:registration_id>/', views.delete_student, name='delete_student'),
    path('edit_student/<int:registration_id>/', views.edit_student_form, name='edit_student_form'),
    path('update_student/<int:old_registration_id>/', views.update_student, name='update_student'),
]
