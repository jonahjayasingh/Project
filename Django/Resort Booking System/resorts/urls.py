from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Customer
    path('resorts/', views.resort_list, name='resort_list'),
    path('resorts/<int:resort_id>/', views.resort_detail, name='resort_detail'),
    path('resorts/<int:resort_id>/rooms/', views.room_list, name='room_list'),
    path('resorts/<int:resort_id>/book/', views.book_resort, name='book_resort'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('resort/<int:resort_id>/review/', views.add_review, name='add_review'),
    path('booking/<int:booking_id>/pay/', views.complete_payment, name='complete_payment'),
    path('register-resort/', views.register_resort, name='register_resort'),

    # Owner
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('resort-dashboard/<int:resort_id>/', views.resort_dashboard, name='resort_dashboard'),
    path('resort/<int:resort_id>/report/', views.report_resort, name='report_resort'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('resort/add/', views.resort_create, name='resort_create'),
    path('owner/resort/<int:pk>/edit/', views.resort_update, name='resort_update'),
    path('owner/resort/<int:pk>/delete/', views.resort_delete, name='resort_delete'),
    path('admin/resort/<int:pk>/approve/', views.approve_resort, name='approve_resort'),
    path('admin/resort/<int:pk>/toggle-status/', views.toggle_resort_status, name='toggle_resort_status'),
    path('admin/resort/<int:pk>/delete-permanent/', views.resort_delete_admin, name='resort_delete_admin'),
    path('admin/resort/<int:resort_id>/room/add/', views.room_create, name='room_create'),
    path('admin/room/<int:pk>/edit/', views.room_update, name='room_update'),
    path('admin/room/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('admin/bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('admin/bookings/<int:booking_id>/status/<str:status>/', views.change_booking_status, name='change_booking_status'),
    path('admin/check-in/', views.check_in_verification, name='check_in_verification'),
    path('admin/monitor/', views.admin_resort_monitor, name='admin_resort_monitor'),
    path('admin/reports/', views.reports_page, name='reports_page'),
]
