from django.db import models
from django.conf import settings
from food.models import MenuItem
from services.models import Service

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True, blank=True)
    guest_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    food_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    service_item = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    customization = models.TextField(blank=True)
    
    def subtotal(self):
        if self.food_item:
            # Food is priced per guest (plate)
            return self.food_item.price * self.cart.guest_count
        if self.service_item:
            # Services are priced by quantity (e.g. 2 photographers)
            return self.service_item.base_price * self.quantity
        return 0
