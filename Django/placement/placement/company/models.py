from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CompanyDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100,unique=True)
    location = models.CharField(max_length=100)
    industry_type = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="CompanyProfilePicture",null=True,blank= True)

   


class JobDetails(models.Model):
    company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    salary = models.FloatField()
    location = models.CharField(max_length=100)
    industry_type = models.CharField(max_length=100)
    cgpa_threshold = models.FloatField(null=True,blank=True)
    job_type = models.CharField(max_length=100)
    job_mode = models.CharField(max_length=100)
    resume = models.FileField(upload_to="Resume")
    date_posted = models.DateField()
    is_active = models.BooleanField(default=True)