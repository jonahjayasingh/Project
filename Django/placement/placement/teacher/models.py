from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TeacherDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="TeacherProfilePicture",null=True,blank= True)
    designation = models.CharField(max_length=100,null=True,blank=True)
    department = models.CharField(max_length=100,null=True,blank=True)
    is_hod = models.BooleanField(default=False)
    is_placement_faculty = models.BooleanField(default=False)
