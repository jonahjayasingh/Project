from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='event_list'),
    path('create/', views.event_create_view, name='event_create'),
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    path('<int:pk>/update/', views.event_update_view, name='event_update'),
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),
    
    # Admin
    path('admin/all/', views.admin_all_events_view, name='admin_all_events'),
    path('admin/types/', views.admin_event_types_view, name='admin_event_types'),
    path('admin/types/<int:pk>/edit/', views.admin_event_type_update, name='admin_event_type_update'),
    path('admin/types/<int:pk>/delete/', views.admin_event_type_delete, name='admin_event_type_delete'),
]
