from django.db import models
from django.conf import settings

class Department(models.Model):
    """
    Hospital Department model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='department_head'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    """
    Doctor profile model with specialization and availability
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_id = models.CharField(max_length=20, unique=True, editable=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField(help_text="Medical degrees and certifications")
    experience_years = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=50, unique=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Availability
    available_days = models.CharField(
        max_length=100, 
        help_text="e.g., Monday, Wednesday, Friday",
        blank=True,
        null=True
    )
    available_time_start = models.TimeField(blank=True, null=True)
    available_time_end = models.TimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
        indexes = [
            models.Index(fields=['doctor_id']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            # Generate doctor ID
            last_doctor = Doctor.objects.order_by('-id').first()
            if last_doctor:
                last_id = int(last_doctor.doctor_id.split('-')[1])
                self.doctor_id = f"DOC-{last_id + 1:05d}"
            else:
                self.doctor_id = "DOC-00001"
        super().save(*args, **kwargs)
