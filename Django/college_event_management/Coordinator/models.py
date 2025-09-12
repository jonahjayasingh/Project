from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=255, null=True,blank=True)
    address = models.CharField(max_length=255, null=True,blank=True)
    profile_pic = models.ImageField(upload_to="profile", null=True,blank=True)


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


class Mcq(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="mcqs")
    mcq_title = models.CharField(max_length=255)
    mcq_duration = models.IntegerField()
    is_active = models.BooleanField(default=True)
    no_of_questions = models.IntegerField()
    date = models.DateTimeField(auto_now_add=False,blank=True,null=True)

    def __str__(self):
        return self.mcq_title


class Question(models.Model):
    mcq = models.ForeignKey(Mcq,on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    def get_options(self):
        return [self.option1, self.option2, self.option3, self.option4]