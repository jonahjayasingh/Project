from django.db import models
from django.conf import settings
from patients.models import Patient
from appointments.models import Appointment
from pharmacy.models import Prescription

class Bill(models.Model):
    """
    Billing model for patient invoices
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('online', 'Online Transfer'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    )
    
    bill_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills'
    )
    
    # Bill Details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment Information
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_bills'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bill_id']),
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.bill_id} - {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.bill_id:
            # Generate bill ID
            last_bill = Bill.objects.order_by('-id').first()
            if last_bill:
                last_id = int(last_bill.bill_id.split('-')[1])
                self.bill_id = f"BILL-{last_id + 1:05d}"
            else:
                self.bill_id = "BILL-00001"
        super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        return (
            self.consultation_fee +
            self.medicine_charges +
            self.room_charges +
            self.lab_charges +
            self.other_charges
        )
    
    @property
    def total_amount(self):
        return self.subtotal - self.discount + self.tax
    
    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid


class Payment(models.Model):
    """
    Payment transaction model
    """
    payment_id = models.CharField(max_length=20, unique=True, editable=False)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Bill.PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments'
    )
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_id} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate payment ID
            last_payment = Payment.objects.order_by('-id').first()
            if last_payment:
                last_id = int(last_payment.payment_id.split('-')[1])
                self.payment_id = f"PAY-{last_id + 1:05d}"
            else:
                self.payment_id = "PAY-00001"
        
        # Update bill's amount_paid
        super().save(*args, **kwargs)
        
        # Recalculate total amount paid for the bill
        total_paid = self.bill.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.bill.amount_paid = total_paid
        
        # Update payment status
        if total_paid >= self.bill.total_amount:
            self.bill.payment_status = 'paid'
        elif total_paid > 0:
            self.bill.payment_status = 'partial'
        else:
            self.bill.payment_status = 'pending'
        
        self.bill.save()
