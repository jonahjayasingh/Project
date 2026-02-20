from django.db import models
from django.conf import settings
from doctors.models import Department
from patients.models import Patient

class Nurse(models.Model):
    """
    Nurse profile model
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    )
    
    SHIFT_CHOICES = (
        ('morning', 'Morning (6 AM - 2 PM)'),
        ('afternoon', 'Afternoon (2 PM - 10 PM)'),
        ('night', 'Night (10 PM - 6 AM)'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nurse_profile')
    nurse_id = models.CharField(max_length=20, unique=True, editable=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='nurses')
    qualifications = models.TextField(help_text="Nursing degrees and certifications")
    license_number = models.CharField(max_length=50, unique=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='morning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
        indexes = [
            models.Index(fields=['nurse_id']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"
    
    def save(self, *args, **kwargs):
        if not self.nurse_id:
            # Generate nurse ID
            last_nurse = Nurse.objects.order_by('-id').first()
            if last_nurse:
                last_id = int(last_nurse.nurse_id.split('-')[1])
                self.nurse_id = f"NUR-{last_id + 1:05d}"
            else:
                self.nurse_id = "NUR-00001"
        super().save(*args, **kwargs)


class NursePatientAssignment(models.Model):
    """
    Model to assign nurses to patients
    """
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='patient_assignments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nurse_assignments')
    assigned_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-assigned_date']
        unique_together = ['nurse', 'patient', 'assigned_date']
    
    def __str__(self):
        return f"{self.nurse.user.get_full_name()} assigned to {self.patient.user.get_full_name()}"
