from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='event_list'),
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    path('create/', views.event_create_view, name='event_create'),
    path('<int:pk>/update/', views.event_update_view, name='event_update'),
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),
]
