from django.db import models
from django.conf import settings

class Patient(models.Model):
    """
    Patient model with personal details and medical history
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('discharged', 'Discharged'),
        ('deceased', 'Deceased'),
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
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Medical History
    allergies = models.TextField(blank=True, null=True, help_text="List any allergies")
    chronic_conditions = models.TextField(blank=True, null=True, help_text="List chronic conditions")
    current_medications = models.TextField(blank=True, null=True, help_text="Current medications")
    past_surgeries = models.TextField(blank=True, null=True, help_text="Past surgical history")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    admission_date = models.DateField(blank=True, null=True)
    discharge_date = models.DateField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate patient ID
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient:
                last_id = int(last_patient.patient_id.split('-')[1])
                self.patient_id = f"PAT-{last_id + 1:05d}"
            else:
                self.patient_id = "PAT-00001"
        super().save(*args, **kwargs)


class PatientDocument(models.Model):
    """
    Model for storing patient documents (reports, scans, etc.)
    """
    DOCUMENT_TYPE_CHOICES = (
        ('lab_report', 'Lab Report'),
        ('scan', 'Scan/X-Ray'),
        ('prescription', 'Prescription'),
        ('discharge_summary', 'Discharge Summary'),
        ('other', 'Other'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='patient_documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.title}"
