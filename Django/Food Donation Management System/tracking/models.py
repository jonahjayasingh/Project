from django.db import models
from django.conf import settings
from donations.models import Donation

class StatusHistory(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Status Histories'

    def __str__(self):
        return f"{self.donation.id} - {self.status} - {self.created_at}"
