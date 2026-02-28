from django.db import models
from events.models import Event

class Payment(models.Model):
    PAYMENT_TYPE = [
        ('ADVANCE', 'Advance Payment'),
        ('BALANCE', 'Balance Payment'),
        ('FULL', 'Full Payment'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.payment_type} for {self.event}"
