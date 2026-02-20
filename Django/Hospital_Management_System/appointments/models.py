from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from patients.models import Patient
from doctors.models import Doctor
from datetime import datetime, timedelta

class Appointment(models.Model):
    """
    Appointment model for managing patient-doctor appointments
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    appointment_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField(help_text="Reason for appointment")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    
    # Booking information
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='booked_appointments'
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    
    # Cancellation information
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_id']),
            models.Index(fields=['appointment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['doctor', 'appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate appointment ID
            last_appointment = Appointment.objects.order_by('-id').first()
            if last_appointment:
                last_id = int(last_appointment.appointment_id.split('-')[1])
                self.appointment_id = f"APT-{last_id + 1:05d}"
            else:
                self.appointment_id = "APT-00001"
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Validate that there are no overlapping appointments for the same doctor
        """
        if self.appointment_date and self.appointment_time:
            # Calculate end time
            start_datetime = datetime.combine(self.appointment_date, self.appointment_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
            
            # Check for overlapping appointments
            overlapping = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                status__in=['scheduled', 'confirmed']
            ).exclude(pk=self.pk)
            
            for apt in overlapping:
                apt_start = datetime.combine(apt.appointment_date, apt.appointment_time)
                apt_end = apt_start + timedelta(minutes=apt.duration_minutes)
                
                # Check if times overlap
                if (start_datetime < apt_end and end_datetime > apt_start):
                    raise ValidationError(
                        f"This appointment overlaps with another appointment at {apt.appointment_time}"
                    )
