from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser with additional fields
    for gym management system
    """
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('trainer', 'Trainer'),
        ('member', 'Member'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_staff_member(self):
        return self.role == 'staff'
    
    def is_trainer(self):
        return self.role == 'trainer'
    
    def is_member(self):
        return self.role == 'member'
