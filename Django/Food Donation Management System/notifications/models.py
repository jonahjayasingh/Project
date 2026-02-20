from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('donation_created', 'Donation Created'),
        ('donation_accepted', 'Donation Accepted'),
        ('donation_rejected', 'Donation Rejected'),
        ('volunteer_assigned', 'Volunteer Assigned'),
        ('donation_picked', 'Donation Picked'),
        ('donation_delivered', 'Donation Delivered'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
