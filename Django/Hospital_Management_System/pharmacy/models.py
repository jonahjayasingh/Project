from django.db import models
from django.conf import settings
from medical_records.models import MedicalRecord
from patients.models import Patient
from doctors.models import Doctor

class Medicine(models.Model):
    """
    Medicine inventory model
    """
    CATEGORY_CHOICES = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('other', 'Other'),
    )
    
    medicine_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    manufacturer = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Stock Information
    stock_quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Minimum stock level before reorder")
    
    # Additional Information
    expiry_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['medicine_id']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.generic_name})"
    
    def save(self, *args, **kwargs):
        if not self.medicine_id:
            # Generate medicine ID
            last_medicine = Medicine.objects.order_by('-id').first()
            if last_medicine:
                last_id = int(last_medicine.medicine_id.split('-')[1])
                self.medicine_id = f"MED-{last_id + 1:05d}"
            else:
                self.medicine_id = "MED-00001"
        super().save(*args, **kwargs)
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level


class Prescription(models.Model):
    """
    Prescription model linking medical records with medicines
    """
    prescription_id = models.CharField(max_length=20, unique=True, editable=False)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    
    prescription_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Special instructions")
    
    # Status
    is_dispensed = models.BooleanField(default=False)
    dispensed_at = models.DateTimeField(blank=True, null=True)
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensed_prescriptions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prescription_id']),
            models.Index(fields=['patient', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.prescription_id} - {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            # Generate prescription ID
            last_prescription = Prescription.objects.order_by('-id').first()
            if last_prescription:
                last_id = int(last_prescription.prescription_id.split('-')[1])
                self.prescription_id = f"PRE-{last_id + 1:05d}"
            else:
                self.prescription_id = "PRE-00001"
        super().save(*args, **kwargs)


class PrescriptionItem(models.Model):
    """
    Individual medicine items in a prescription
    """
    FREQUENCY_CHOICES = (
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('other', 'Other'),
    )
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg, 2 tablets")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days = models.PositiveIntegerField(help_text="Duration in days")
    quantity = models.PositiveIntegerField(help_text="Total quantity to dispense")
    instructions = models.TextField(blank=True, null=True, help_text="e.g., Take after meals")
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.medicine.name} - {self.dosage}"
