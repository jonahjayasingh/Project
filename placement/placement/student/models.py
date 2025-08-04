from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class StudentDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="StudentProfilePicture",null=True,blank= True)
    course = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    sem = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=100,unique=True)
    cgpa = models.FloatField(null=True,blank=True)