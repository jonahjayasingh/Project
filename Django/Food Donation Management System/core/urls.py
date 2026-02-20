from django.contrib import admin
from django.urls import path, include
from accounts.views import home_view

urlpatterns = [
    path('admin_django/', admin.site.urls), # Renamed to avoid confusion with our admin dashboard
    path('accounts/', include('accounts.urls')),
    path('donations/', include('donations.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('', home_view, name='home'), 
]
