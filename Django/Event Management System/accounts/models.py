from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role-based authentication.
    Roles: ADMIN and CLIENT
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='CLIENT',
        help_text='User role for access control'
    )
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'ADMIN'
    
    def is_client(self):
        """Check if user is a client"""
        return self.role == 'CLIENT'
