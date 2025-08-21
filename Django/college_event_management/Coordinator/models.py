from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Gallery(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="galary")
    image = models.ImageField(upload_to="galary")
    date = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=255,default="")
    gallery_type = models.CharField(max_length=255,default="")


class Events(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="events")
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    event_location = models.CharField(max_length=255)
    event_description = models.TextField()
    event_image = models.ImageField(upload_to="events")
