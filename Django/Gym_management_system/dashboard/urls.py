from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('member/', views.member_dashboard, name='member_dashboard'),
    path('trainer/', views.trainer_dashboard, name='trainer_dashboard'),
]
