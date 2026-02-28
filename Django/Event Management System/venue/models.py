from django.db import models
from events.models import Event

class VenueDetails(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='venue_details')
    venue_name = models.CharField(max_length=200)
    welcome_drinks = models.BooleanField(default=False)
    room_arrangement_bride_groom = models.BooleanField(default=False)
    additional_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Venue for {self.event}"
