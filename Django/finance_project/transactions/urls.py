from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('reports/', views.reports, name='reports'),
    path('export/', views.export_transactions, name='export_transactions'),
    path('register/', views.register, name='register'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-account/', views.add_account, name='add_account'),
    path('manage/', views.manage_data, name='manage_data'),
    path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('account/<int:pk>/edit/', views.edit_account, name='edit_account'),
    path('account/<int:pk>/delete/', views.delete_account, name='delete_account'),
    path('transaction/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transaction/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
]
