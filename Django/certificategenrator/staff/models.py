from django.db import models
from django.contrib.auth.models import User
from app.models import Student
# Create your models here.

class Work(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    time_slot = models.CharField(max_length=100)
    work = models.TextField(default="",blank=True,null=True)
    date = models.DateField(auto_now_add=False,blank=True,null=True)

    
    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    date = models.DateField(blank=True,null=True)