from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    path('', views.guest_list_view, name='guest_list'),
    path('create/', views.guest_create_view, name='guest_create'),
    path('<int:pk>/delete/', views.guest_delete_view, name='guest_delete'),
]
