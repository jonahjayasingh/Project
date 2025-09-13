from os import name
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

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
