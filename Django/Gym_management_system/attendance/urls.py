from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('check-in/', views.check_in, name='check_in'),
    path('<int:pk>/check-out/', views.check_out, name='check_out'),
]
