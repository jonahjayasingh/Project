from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/member/', views.member_login, name='member_login'),
    path('login/trainer/', views.trainer_login, name='trainer_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
]
