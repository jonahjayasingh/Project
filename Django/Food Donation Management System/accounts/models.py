from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('ngo', 'NGO'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    
    # Location fields for volunteers and NGOs
    address = models.TextField(blank=True, null=True, help_text="Your location address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Longitude coordinate")

    def __str__(self):
        return f"{self.username} ({self.role})"
