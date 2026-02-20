from django.db import models
from django.utils import timezone
import uuid


class Payment(models.Model):
    """
    Track all payments made by members
    """
    
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
    )
    
    TYPE_CHOICES = (
        ('membership', 'Membership Fee'),
        ('personal_training', 'Personal Training'),
        ('class_fee', 'Class Fee'),
        ('registration', 'Registration Fee'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='membership')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="For online payments")
    payment_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='received_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.member.user.get_full_name()} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate unique invoice number
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    Store generated invoices for payments
    """
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"Invoice for {self.payment.invoice_number}"
