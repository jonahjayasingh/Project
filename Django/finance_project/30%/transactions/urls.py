from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('register/', views.register, name='register'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
]
