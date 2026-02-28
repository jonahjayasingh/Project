from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/', views.add_to_cart_view, name='add_to_cart'),
    path('update-quantity/<int:item_id>/', views.update_item_quantity_view, name='update_item_quantity'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('remove-food/<int:food_id>/', views.remove_food_view, name='remove_food'),
    path('remove-service/<int:service_id>/', views.remove_service_view, name='remove_service'),
    path('update-guests/', views.update_guest_count_view, name='update_guest_count'),
    path('finalize/', views.finalize_booking_view, name='finalize'),
]
