from django.db import models
from django.conf import settings

class EventType(models.Model):
    """
    Types of events: Puberty, Birthday, Marriage
    """
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='event_types/')

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Event model for managing client events.
    """
    EVENT_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    venue_location = models.CharField(max_length=300)
    
    # Client Details (can be redundant if user profile has it, but requested specifically)
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=20)
    client_email = models.EmailField()

    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='PENDING')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    advance_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_type.name if self.event_type else 'N/A'} - {self.client_name} ({self.date})"

    @property
    def remaining_balance(self):
        return self.total_cost - self.advance_paid

    @property
    def payment_status(self):
        if self.advance_paid == 0:
            return "Unpaid"
        elif self.advance_paid < self.total_cost:
            return "Partially Paid (Advance)"
        else:
            return "Fully Paid"

class EventSelection(models.Model):
    """
    Persists the selected food and services for an event.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='selections')
    
    # Can be either food or service
    food_item = models.ForeignKey('food.MenuItem', on_delete=models.CASCADE, null=True, blank=True)
    service_item = models.ForeignKey('services.Service', on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2) # Price at time of booking
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        item_name = self.food_item.name if self.food_item else self.service_item.name
        return f"{item_name} for {self.event.client_name}'s {self.event.event_type.name}"
