from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('create/', views.member_create, name='member_create'),
    path('<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('<int:pk>/delete/', views.member_delete, name='member_delete'),
]
