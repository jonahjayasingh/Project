from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    path('menu/', views.menu_list_view, name='menu_list'),
    path('admin/menus/', views.admin_menus_view, name='admin_menus'),
    path('admin/menus/add/', views.menu_item_create, name='menu_item_create'),
    path('admin/menus/<int:pk>/edit/', views.menu_item_update, name='menu_item_update'),
    path('admin/menus/<int:pk>/delete/', views.menu_item_delete, name='menu_item_delete'),
]
