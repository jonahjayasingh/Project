from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list_view, name='booking_list'),
    path('create/', views.booking_create_view, name='booking_create'),
    path('<int:pk>/delete/', views.booking_delete_view, name='booking_delete'),
]
