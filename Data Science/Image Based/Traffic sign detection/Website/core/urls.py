from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('predict-image/', views.predict_image, name='predict_image'),
    path('predict-video/', views.predict_video_page, name='predict_video_page'),
    path('predict-frame/', views.predict_frame, name='predict_frame'),
]
