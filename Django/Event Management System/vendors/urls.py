from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.vendor_list_view, name='vendor_list'),
    path('create/', views.vendor_create_view, name='vendor_create'),
    path('<int:pk>/update/', views.vendor_update_view, name='vendor_update'),
    path('<int:pk>/delete/', views.vendor_delete_view, name='vendor_delete'),
]
