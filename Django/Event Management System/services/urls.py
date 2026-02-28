from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list_view, name='service_list'),
    path('admin/', views.admin_services_view, name='admin_services'),
    path('admin/add/', views.service_create, name='service_create'),
    path('admin/<int:pk>/edit/', views.service_update, name='service_update'),
    path('admin/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('admin/<int:pk>/portfolio/', views.service_portfolio_manage, name='service_portfolio_manage'),
    path('admin/portfolio/<int:pk>/delete/', views.service_portfolio_delete, name='service_portfolio_delete'),
]
