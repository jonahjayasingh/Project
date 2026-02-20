from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    # Trainer CRUD
    path('', views.trainer_list, name='trainer_list'),
    path('<int:pk>/', views.trainer_detail, name='trainer_detail'),
    path('create/', views.trainer_create, name='trainer_create'),
    path('<int:pk>/edit/', views.trainer_edit, name='trainer_edit'),
    path('<int:pk>/delete/', views.trainer_delete, name='trainer_delete'),
    
    # Availability management
    path('<int:trainer_pk>/availability/add/', views.availability_create, name='availability_create'),
    path('availability/<int:pk>/delete/', views.availability_delete, name='availability_delete'),
    
    # Assignment management
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/update/', views.assignment_update, name='assignment_update'),
]
