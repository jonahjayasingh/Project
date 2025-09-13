from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class JobPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=200)
    experience = models.CharField(max_length=200)
    description = models.TextField()
    last_date = models.DateField()
    salary = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)


class CompanyProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="companyprofile")
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_description = models.TextField()
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)


class JobSeekerProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="jobseekerprofile")
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

class JobApplication(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    ats_score = models.FloatField(default=0.0)

