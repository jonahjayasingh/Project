from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # No Django admin usage
    path('', include('core.urls')),
]
