from django.db import models
from django.conf import settings

class Event(models.Model):
    """
    Event model for managing client events.
    Each event is created by a client user.
    """
    name = models.CharField(max_length=200, help_text='Event name')
    date = models.DateField(help_text='Event date')
    venue = models.CharField(max_length=300, help_text='Event venue/location')
    expected_guests = models.PositiveIntegerField(
        default=0,
        help_text='Expected number of guests'
    )
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Total event budget'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        help_text='Client who created this event'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    def total_bookings_cost(self):
        """Calculate total cost of all bookings for this event"""
        return sum(booking.price for booking in self.bookings.all())
    
    def remaining_budget(self):
        """Calculate remaining budget after bookings"""
        return self.budget - self.total_bookings_cost()
