from django.db import models
from events.models import Event
from vendors.models import Vendor

class Booking(models.Model):
    """
    Booking model for managing vendor bookings for events.
    Prevents duplicate bookings for same vendor on same event date.
    """
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Event for this booking'
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Vendor being booked'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Booking price (copied from vendor)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Booked',
        help_text='Booking status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        # Ensure unique booking: one vendor per event
        unique_together = ['event', 'vendor']
    
    def __str__(self):
        return f"{self.event.name} - {self.vendor.name}"
    
    def save(self, *args, **kwargs):
        """Auto-populate price from vendor if not set"""
        if not self.price:
            self.price = self.vendor.price
        super().save(*args, **kwargs)
