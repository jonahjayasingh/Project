from os import name
from django.db import models
from django.contrib.auth.models import User
# Create your models here.from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Constant_Value(models.Model):
    certificate_id = models.PositiveBigIntegerField()
    receipt_reg_no = models.PositiveBigIntegerField()
    registration_no = models.PositiveBigIntegerField()

class GetInTouch(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    message = models.TextField()

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    registration_no = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    total_fee = models.PositiveIntegerField()
    course_name = models.CharField(max_length=100)
    phone = models.PositiveIntegerField()
    email = models.EmailField()
    dob = models.DateField(null=True,blank=True)
    joined_date = models.DateField(null=True,blank=True)
    faculty_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address = models.TextField()
    qualification = models.CharField(max_length=255, null=True,blank=True)
    marital_status = models.CharField(max_length=255, null=True,blank=True)
    online = models.BooleanField(null=True,blank=True)
    project_title = models.TextField(null=True,blank=True)
    date_range = models.CharField(max_length=400,null=True,blank=True) 
    completed_date = models.DateField(null=True,blank=True)
    certificate_type = models.CharField(max_length=100, null=True,blank=True)
    certificate_id = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.name

class StaffPermission(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    receipt_permission = models.BooleanField(default=False)
    certificate_permission = models.BooleanField(default=False)
    student_permission = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class Receipt(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receipts')
    amount = models.PositiveIntegerField()
    date = models.DateField()
    reg_no = models.CharField(max_length=100)

    
    def __str__(self):
        return self.name


class Payment(models.Model):
    user = models.ForeignKey(Student,on_delete=models.CASCADE,related_name="payment")
    paid_ammount = models.PositiveIntegerField()
    def __str__(self):
        return self.user.name + " - " + str(self.paid_ammount)
    

class Account(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    account_balance = models.PositiveBigIntegerField()

    def __str__(self):
        return f" {self.amount} - {self.timestamp}"

class CourseName(models.Model):
    course_name = models.CharField(max_length=500)

    def __str__(self):
        return self.course_name
    
class StaffDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    photo= models.ImageField(upload_to="staff_photo",null=True,blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    pincode = models.CharField(max_length=100)
    designation = models.CharField(max_length=500)
    joining_date = models.DateField()
    dob = models.DateField()
    salary = models.PositiveIntegerField()
    employee_id = models.PositiveIntegerField()
    resignation_date = models.DateField(null=True,blank=True)
    documents = models.TextField(null=True,blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk and self.user:
            self.name = self.user.username
            self.email = self.user.email
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Website_Course(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="course")
    course_name = models.CharField(max_length=500)
    course_description = models.TextField()
    course_duration = models.CharField(max_length=500)
    course_price = models.PositiveIntegerField()
    course_difficulty = models.CharField(max_length=500)
    course_thumbnail = models.ImageField(upload_to="course_thumbnail",null=True,blank=True)
    
    def __str__(self):
        return self.course_name
    
class Website_Gallery(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="gallery")
    gallery_title = models.CharField(max_length=500)
    gallery_image = models.ImageField(upload_to="gallery_image",null=True,blank=True)

class website_Placement(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    description = models.TextField()
    job_title = models.CharField(max_length=500)
    job_company = models.CharField(max_length=500)
    image = models.ImageField(upload_to="placement_thumbnail",null=True,blank=True)

    def __str__(self):
        return self.name

class website_services(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="services")
    name = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ImageField(upload_to="service_thumbnail",null=True,blank=True)
    key_points = models.JSONField()

    def __str__(self):
        return self.name


    
class website_project_domain(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="domain")
    name = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ImageField(upload_to="domain_thumbnail",null=True,blank=True)

    def __str__(self):
        return self.name
    
class website_project(models.Model):
    domain = models.ForeignKey(website_project_domain,on_delete=models.CASCADE,related_name="project")
    name = models.CharField(max_length=500)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class company_contacts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="contact")
    phone1 = models.PositiveBigIntegerField()
    phone2 = models.PositiveBigIntegerField(null=True,blank=True)
    email = models.EmailField()
    whatsapp = models.PositiveBigIntegerField()
    address = models.TextField(null=True,blank=True)
    linkedin = models.URLField(null=True,blank=True)
    twitter = models.URLField(null=True,blank=True)
    facebook = models.URLField(null=True,blank=True)
    instagram = models.URLField(null=True,blank=True)
    youtube = models.URLField(null=True,blank=True)
    map_embed_url = models.TextField(null=True,blank=True)


class company_career(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="career")
    title = models.CharField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=500)
    
    application_Deadline = models.DateField()
    job_type = models.CharField(max_length=500)
    experience = models.CharField(max_length=500)
    key_responsibilities = models.JSONField()

    def __str__(self):
        return self.title

class company_applicant(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField()
    phone = models.PositiveBigIntegerField()
    experience = models.CharField(max_length=500)
    current_company = models.CharField(max_length=500,null=True,blank=True)
    resume = models.FileField(upload_to="ApplicantResume")
    cover_letter = models.TextField(null=True,blank=True)
    career = models.ForeignKey(company_career,on_delete=models.CASCADE,related_name="applicant")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def delete(self, *args, **kwargs):
        # Delete the file first
        print(self.first_name)
        if self.resume:
            self.resume.delete(save=False)
        # Then delete the model instance
        super().delete(*args, **kwargs)

@receiver(post_delete, sender=company_applicant)
def delete_resume_file(sender, instance, **kwargs):
    """Delete resume file from storage when applicant is deleted."""
    if instance.resume:
        instance.resume.delete(save=False)