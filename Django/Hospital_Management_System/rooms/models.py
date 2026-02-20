from django.db import models
from django.conf import settings
from patients.models import Patient

class Room(models.Model):
    """
    Hospital room model
    """
    ROOM_TYPE_CHOICES = (
        ('general', 'General Ward'),
        ('semi_private', 'Semi-Private'),
        ('private', 'Private'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('operation', 'Operation Theater'),
    )
    
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    floor = models.PositiveIntegerField()
    cost_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['room_type']),
        ]
    
    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()}"
    
    @property
    def total_beds(self):
        return self.beds.count()
    
    @property
    def available_beds(self):
        return self.beds.filter(is_occupied=False).count()


class Bed(models.Model):
    """
    Hospital bed model
    """
    bed_number = models.CharField(max_length=20)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    is_occupied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['room', 'bed_number']
        unique_together = ['room', 'bed_number']
    
    def __str__(self):
        return f"Bed {self.bed_number} in {self.room.room_number}"


class Admission(models.Model):
    """
    Patient admission model
    """
    STATUS_CHOICES = (
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    )
    
    admission_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, related_name='admissions')
    
    # Admission Details
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(blank=True, null=True)
    reason = models.TextField(help_text="Reason for admission")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='admitted')
    
    # Staff Information
    admitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admitted_patients'
    )
    discharged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discharged_patients'
    )
    
    # Discharge Information
    discharge_summary = models.TextField(blank=True, null=True)
    discharge_instructions = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-admission_date']
        indexes = [
            models.Index(fields=['admission_id']),
            models.Index(fields=['patient', '-admission_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.admission_id} - {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.admission_id:
            # Generate admission ID
            last_admission = Admission.objects.order_by('-id').first()
            if last_admission:
                last_id = int(last_admission.admission_id.split('-')[1])
                self.admission_id = f"ADM-{last_id + 1:05d}"
            else:
                self.admission_id = "ADM-00001"
        
        # Update bed occupancy
        if self.bed:
            if self.status == 'admitted':
                self.bed.is_occupied = True
            else:
                self.bed.is_occupied = False
            self.bed.save()
        
        super().save(*args, **kwargs)
    
    @property
    def duration_days(self):
        if self.discharge_date:
            return (self.discharge_date - self.admission_date).days
        else:
            from django.utils import timezone
            return (timezone.now() - self.admission_date).days
