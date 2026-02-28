from django.db import models
from events.models import Event

class Feedback(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.event} - {self.rating} Stars"
