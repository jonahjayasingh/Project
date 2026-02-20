from django.db import models
from django.conf import settings


class Member(models.Model):
    """
    Extended member profile with additional information
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('frozen', 'Frozen'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_profile')
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True, help_text="Any medical conditions or allergies")
    join_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    fitness_goal = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['-join_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_status_display()}"
    
    def get_active_membership(self):
        """Get the current active membership"""
        from memberships.models import MemberMembership
        return MemberMembership.objects.filter(
            member=self,
            status='active'
        ).first()
