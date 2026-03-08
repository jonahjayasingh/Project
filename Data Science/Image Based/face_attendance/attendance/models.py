from django.db import models
from datetime import datetime

class StudentData(models.Model):
    registration_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    image = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(StudentData, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=datetime.today)
    time = models.TimeField(default=datetime.now)

    @property
    def Name(self):
        return self.student.name

    def __str__(self):
        return f"{self.student.name} - {self.date}"
