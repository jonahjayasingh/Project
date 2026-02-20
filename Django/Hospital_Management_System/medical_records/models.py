from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

class MedicalRecord(models.Model):
    """
    Medical record model for storing patient diagnosis and treatment
    """
    record_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records')
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='medical_records'
    )
    
    # Medical Information
    symptoms = models.TextField(help_text="Patient symptoms")
    diagnosis = models.TextField(help_text="Doctor's diagnosis")
    treatment_plan = models.TextField(help_text="Recommended treatment")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="°F")
    blood_pressure = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 120/80")
    pulse_rate = models.PositiveIntegerField(blank=True, null=True, help_text="beats per minute")
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True, help_text="breaths per minute")
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="%")
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['record_id']),
            models.Index(fields=['patient', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.record_id} - {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.record_id:
            # Generate record ID
            last_record = MedicalRecord.objects.order_by('-id').first()
            if last_record:
                last_id = int(last_record.record_id.split('-')[1])
                self.record_id = f"MED-{last_id + 1:05d}"
            else:
                self.record_id = "MED-00001"
        super().save(*args, **kwargs)


class LabReport(models.Model):
    """
    Lab report model for storing test results
    """
    TEST_TYPE_CHOICES = (
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct_scan', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    )
    
    report_id = models.CharField(max_length=20, unique=True, editable=False)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_reports')
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=200)
    test_date = models.DateField()
    results = models.TextField()
    file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-test_date']
    
    def __str__(self):
        return f"{self.report_id} - {self.test_name}"
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            # Generate report ID
            last_report = LabReport.objects.order_by('-id').first()
            if last_report:
                last_id = int(last_report.report_id.split('-')[1])
                self.report_id = f"LAB-{last_id + 1:05d}"
            else:
                self.report_id = "LAB-00001"
        super().save(*args, **kwargs)
