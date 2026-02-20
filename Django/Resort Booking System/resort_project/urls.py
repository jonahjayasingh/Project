from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # No standard admin panel as requested, but keeping it for emergencies if needed
    # path('admin/', admin.site.urls), 
    path('', include('resorts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
