from django.db import models
from django.utils import timezone
from datetime import timedelta


class MembershipPlan(models.Model):
    """
    Membership plans offered by the gym
    """
    
    DURATION_CHOICES = (
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
    )
    
    ACCESS_LEVEL_CHOICES = (
        ('gym_only', 'Gym Only'),
        ('gym_classes', 'Gym + Classes'),
        ('premium', 'Premium (Gym + Classes + Personal Training)'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_months = models.IntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='gym_only')
    benefits = models.TextField(help_text="List of benefits (one per line)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Membership Plan'
        verbose_name_plural = 'Membership Plans'
        ordering = ['duration_months', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.get_duration_months_display()}"


class MemberMembership(models.Model):
    """
    Tracks member's membership subscriptions
    """
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('frozen', 'Frozen'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
    )
    
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    freeze_start_date = models.DateField(blank=True, null=True)
    freeze_end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Member Membership'
        verbose_name_plural = 'Member Memberships'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.plan.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate end_date if not provided
        if not self.end_date and self.start_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_months * 30)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if membership has expired"""
        return self.end_date < timezone.now().date()
    
    def days_remaining(self):
        """Calculate days remaining in membership"""
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now().date()).days
    
    def freeze_membership(self, freeze_days):
        """Freeze membership for specified days"""
        self.freeze_start_date = timezone.now().date()
        self.freeze_end_date = self.freeze_start_date + timedelta(days=freeze_days)
        self.status = 'frozen'
        # Extend end_date by freeze duration
        self.end_date = self.end_date + timedelta(days=freeze_days)
        self.save()
    
    def unfreeze_membership(self):
        """Unfreeze membership"""
        self.status = 'active'
        self.freeze_start_date = None
        self.freeze_end_date = None
        self.save()
