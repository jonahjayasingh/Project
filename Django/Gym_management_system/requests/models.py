from django.db import models
from django.conf import settings


class MembershipRequest(models.Model):
    """
    Membership requests from prospective members
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')))
    address = models.TextField()
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    # Health Information
    blood_group = models.CharField(max_length=3, choices=(
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ), blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True, help_text="Any medical conditions or allergies")
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    fitness_goal = models.TextField(blank=True, null=True)
    
    # Membership Plan Selection
    selected_plan = models.ForeignKey('memberships.MembershipPlan', on_delete=models.PROTECT, related_name='requests')
    
    # Request Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_membership_requests')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Created user (if approved)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='membership_request')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Membership Request'
        verbose_name_plural = 'Membership Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.selected_plan.name} ({self.get_status_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class TrainerRequest(models.Model):
    """
    Requests from members to be assigned a personal trainer
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='trainer_requests')
    
    # Trainer Preferences
    preferred_specialization = models.CharField(max_length=20, choices=(
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('crossfit', 'CrossFit'),
        ('martial_arts', 'Martial Arts'),
        ('zumba', 'Zumba'),
        ('general', 'General Fitness'),
    ))
    preferred_trainer = models.ForeignKey('trainers.Trainer', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    sessions_per_week = models.IntegerField(default=2, choices=((1, '1 Session'), (2, '2 Sessions'), (3, '3 Sessions'), (4, '4 Sessions'), (5, '5+ Sessions')))
    preferred_time = models.CharField(max_length=20, choices=(
        ('morning', 'Morning (6 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 6 PM)'),
        ('evening', 'Evening (6 PM - 10 PM)'),
    ))
    
    # Goals and Notes
    fitness_goals = models.TextField(help_text="What do you want to achieve with personal training?")
    additional_notes = models.TextField(blank=True, null=True)
    
    # Request Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    assigned_trainer = models.ForeignKey('trainers.Trainer', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_trainer_requests')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trainer Request'
        verbose_name_plural = 'Trainer Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.get_preferred_specialization_display()} ({self.get_status_display()})"
