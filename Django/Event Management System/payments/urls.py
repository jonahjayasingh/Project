from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:event_id>/', views.client_payment_view, name='pay_now'),
    path('stripe/success/', views.stripe_success_view, name='stripe_success'),
    path('admin/ledger/', views.admin_payments_view, name='admin_ledger'),
]
