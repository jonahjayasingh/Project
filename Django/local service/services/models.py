from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    keywords = models.TextField(help_text="Comma separated keywords for NLP detection")
    icon = models.CharField(max_length=50, default="bi-tools", help_text="Bootstrap icon class name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    location_name = models.CharField(max_length=200, help_text="User's home area/city", blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    onboarding_completed = models.BooleanField(default=False)
    
    # Advanced Preferences
    budget_tolerance = models.CharField(max_length=20, default='mid', choices=[('low', 'Budget Focused'), ('mid', 'Value for Money'), ('high', 'Premium Only')])
    distance_tolerance_km = models.IntegerField(default=30)
    quality_priority = models.BooleanField(default=True, help_text="Prefer high rating over low cost")
    favorite_categories = models.ManyToManyField(Category, blank=True, related_name="interested_users")
    
    def __str__(self):
        return self.user.username

    @property
    def recent_categories(self):
        # Derive preferred categories from booking history
        return Category.objects.filter(providers__bookings__user=self.user).distinct()[:3]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.get_or_create(user=instance)

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category, related_name="providers")
    bio = models.TextField()
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    jobs_completed = models.IntegerField(default=0)
    location = models.CharField(max_length=200, help_text="City or Area name")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    profile_image = models.ImageField(upload_to='providers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Intelligence Metrics
    response_speed_minutes = models.IntegerField(default=30, help_text="Avg response time in minutes")
    
    # Responsiveness Metrics
    total_requests = models.IntegerField(default=0)
    accepted_requests = models.IntegerField(default=0)
    cancelled_by_provider = models.IntegerField(default=0)
    no_show_count = models.IntegerField(default=0)
    
    @property
    def acceptance_rate(self):
        if self.total_requests == 0: return 100.0
        return round((self.accepted_requests / self.total_requests) * 100, 1)

    @property
    def cancellation_rate(self):
        if self.accepted_requests == 0: return 0.0
        return round((self.cancelled_by_provider / self.accepted_requests) * 100, 1)

    @property
    def badges(self):
        badges = []
        if self.acceptance_rate > 90 and self.total_requests > 5:
            badges.append("Fast Responder")
        if self.rating >= 4.8 and self.jobs_completed > 10:
            badges.append("Top Rated")
        if self.cancellation_rate < 5 and self.jobs_completed > 5:
            badges.append("Highly Reliable")
        return badges
    


    @property
    def on_time_rate(self):
        # Calculate from reviews
        total_reviews = self.reviews.count()
        if total_reviews == 0:
            return 95.0 # Benchmark for new pros
        on_time_count = self.reviews.filter(was_on_time=True).count()
        return round((on_time_count / total_reviews) * 100, 1)

    @property
    def completion_rate(self):
        # Ratio of Completed vs (Completed + Cancelled)
        stats = self.bookings.exclude(status='PENDING').values_list('status', flat=True)
        if not stats:
            return 98.0 # Benchmark for new pros
        
        total = len(stats)
        completed = list(stats).count('COMPLETED')
        return round((completed / total) * 100, 1)

    def __str__(self):
        cat_names = ", ".join([c.name for c in self.categories.all()])
        return f"{self.name} - {cat_names}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    time_slot = models.CharField(max_length=20) # e.g. "09:00 - 10:00"
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_hours = models.IntegerField(default=2)

    @property
    def total_cost(self):
        return self.provider.price_per_hour * self.estimated_hours

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} with {self.provider.name} on {self.date}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review", null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    was_on_time = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.provider.name} by {self.user.username if self.user else 'Anonymous'}"

class FavoriteProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'provider')

class Notification(models.Model):
    TYPES = [
        ('BOOKING', 'Booking Update'),
        ('REMINDER', 'Appointment Reminder'),
        ('SYSTEM', 'System Alert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username} at {self.created_at}"

class Dispute(models.Model):
    ISSUE_TYPES = [
        ('LATE', 'Late Arrival'),
        ('QUALITY', 'Poor Service Quality'),
        ('BEHAVIOR', 'Unprofessional Behavior'),
        ('COST', 'Price Discrepancy'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_REVIEW', 'In Review'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='dispute')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes')
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES)
    description = models.TextField()
    evidence = models.ImageField(upload_to='disputes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dispute for Booking #{self.booking.id} - {self.get_issue_type_display()}"
