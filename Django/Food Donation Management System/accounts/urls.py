from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('update-location/', views.update_location, name='update_location'),
]
