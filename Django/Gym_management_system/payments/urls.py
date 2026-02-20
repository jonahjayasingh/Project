from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('<int:pk>/refund/', views.payment_refund, name='payment_refund'),
]
