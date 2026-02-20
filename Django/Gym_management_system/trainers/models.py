from django.db import models
from django.conf import settings


class Trainer(models.Model):
    """
    Trainer profile with specialization and availability
    """
    
    SPECIALIZATION_CHOICES = (
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('crossfit', 'CrossFit'),
        ('martial_arts', 'Martial Arts'),
        ('zumba', 'Zumba'),
        ('general', 'General Fitness'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_profile')
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    certifications = models.TextField(help_text="List certifications (one per line)")
    experience_years = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trainer'
        verbose_name_plural = 'Trainers'
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"


class TrainerAvailability(models.Model):
    """
    Trainer's weekly availability schedule
    """
    
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Trainer Availability'
        verbose_name_plural = 'Trainer Availabilities'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['trainer', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.trainer.user.get_full_name()} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"


class TrainerMemberAssignment(models.Model):
    """
    Assignment of trainers to members for personal training
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='member_assignments')
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='trainer_assignments')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    sessions_per_week = models.IntegerField(default=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trainer-Member Assignment'
        verbose_name_plural = 'Trainer-Member Assignments'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.trainer.user.get_full_name()} → {self.member.user.get_full_name()}"
