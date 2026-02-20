from django.db import models
from events.models import Event

class Guest(models.Model):
    """
    Guest model for managing event guest lists.
    Each guest belongs to an event.
    """
    CATEGORY_CHOICES = [
        ('Family', 'Family'),
        ('Friend', 'Friend'),
        ('VIP', 'VIP'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='guests',
        help_text='Event this guest is invited to'
    )
    name = models.CharField(max_length=200, help_text='Guest name')
    contact = models.CharField(
        max_length=100,
        help_text='Guest contact information (phone/email)'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text='Guest category'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category}) - {self.event.name}"
