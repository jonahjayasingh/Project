from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # Fitness Class CRUD
    path('', views.class_list, name='class_list'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('create/', views.class_create, name='class_create'),
    path('<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('<int:pk>/delete/', views.class_delete, name='class_delete'),
    
    # Schedule management
    path('<int:class_pk>/schedule/add/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    
    # Booking management
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]
