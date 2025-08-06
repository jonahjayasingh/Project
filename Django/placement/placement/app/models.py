from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserPermission(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)


class Principal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="principalProfilePicture",null=True,blank= True)    