from django.urls import path
from . import views

urlpatterns = [
    # Donor URLs
    path('donor/', views.donor_dashboard, name='donor_dashboard'),
    path('create/', views.create_donation, name='create_donation'),
    path('detail/<int:donation_id>/', views.donation_detail, name='donation_detail'),
    
    # NGO URLs
    path('ngo/', views.ngo_dashboard, name='ngo_dashboard'),
    path('accept/<int:donation_id>/', views.accept_donation, name='accept_donation'),
    path('reject/<int:donation_id>/', views.reject_donation, name='reject_donation'),
    path('assign/<int:donation_id>/', views.assign_volunteer, name='assign_volunteer'),
    path('cancel-acceptance/<int:donation_id>/', views.cancel_acceptance, name='cancel_acceptance'),
    
    # Volunteer URLs
    path('volunteer/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('mark-picked/<int:donation_id>/', views.mark_picked, name='mark_picked'),
    path('mark-delivered/<int:donation_id>/', views.mark_delivered, name='mark_delivered'),
    
    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('admin/donations/', views.manage_donations, name='manage_donations'),
    path('admin/donations/delete/<int:donation_id>/', views.delete_donation, name='delete_donation'),
    
    # General URLs
    path('list/', views.donation_list, name='donation_list'),
    path('history/', views.donation_history, name='donation_history'),
]
