from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    # Membership Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='plan_delete'),
    
    # Member Memberships
    path('', views.membership_list, name='membership_list'),
    path('create/', views.membership_create, name='membership_create'),
    path('<int:pk>/edit/', views.membership_edit, name='membership_edit'),
    path('<int:pk>/freeze/', views.membership_freeze, name='membership_freeze'),
    path('<int:pk>/unfreeze/', views.membership_unfreeze, name='membership_unfreeze'),
]
