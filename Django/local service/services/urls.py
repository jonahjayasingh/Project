from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search_results'),
    path('provider/<int:pk>/', views.provider_detail, name='provider_detail'),
    path('provider/<int:pk>/book/', views.book_appointment, name='book_appointment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('booking/<int:booking_id>/status/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('review/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('chatbot/', views.ai_chatbot, name='ai_chatbot'),
    path('signup/', views.signup, name='signup'),
    path('become-pro/', views.register_provider, name='register_provider'),
    path('login/', auth_views.LoginView.as_view(template_name='services/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Intelligence & Management
    path('profile/update/', views.update_profile, name='update_profile'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/toggle/<int:provider_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Advanced Features
    path('preferences/', views.update_user_preferences, name='update_preferences'),
    path('booking/<int:booking_id>/dispute/', views.report_dispute, name='report_dispute'),
]
