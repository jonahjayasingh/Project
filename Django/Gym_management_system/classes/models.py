from django.db import models
from django.core.exceptions import ValidationError


class FitnessClass(models.Model):
    """
    Fitness class types offered by the gym
    """
    
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_minutes = models.IntegerField(default=60)
    capacity = models.IntegerField(default=20, help_text="Maximum number of participants")
    image = models.ImageField(upload_to='class_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fitness Class'
        verbose_name_plural = 'Fitness Classes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"


class ClassSchedule(models.Model):
    """
    Weekly schedule for fitness classes
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
    
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='schedules')
    trainer = models.ForeignKey('trainers.Trainer', on_delete=models.SET_NULL, null=True, related_name='class_schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    room_location = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Class Schedule'
        verbose_name_plural = 'Class Schedules'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['fitness_class', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.fitness_class.name} - {self.get_day_of_week_display()} at {self.start_time}"
    
    def get_current_bookings_count(self):
        """Get count of confirmed bookings for this schedule"""
        return self.bookings.filter(status='confirmed').count()
    
    def get_available_slots(self):
        """Get number of available slots"""
        return self.fitness_class.capacity - self.get_current_bookings_count()
    
    def is_full(self):
        """Check if class is at full capacity"""
        return self.get_current_bookings_count() >= self.fitness_class.capacity


class ClassBooking(models.Model):
    """
    Member bookings for fitness classes
    """
    
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('waitlist', 'Waitlist'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    )
    
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='bookings')
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='class_bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Class Booking'
        verbose_name_plural = 'Class Bookings'
        ordering = ['-booking_date']
        unique_together = ['schedule', 'member']
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.schedule.fitness_class.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-assign to waitlist if class is full
        if not self.pk:  # New booking
            if self.schedule.is_full() and self.status == 'confirmed':
                self.status = 'waitlist'
        super().save(*args, **kwargs)
    
    def cancel_booking(self):
        """Cancel this booking and promote waitlist if applicable"""
        self.status = 'cancelled'
        self.save()
        
        # Promote first person from waitlist
        waitlist_booking = ClassBooking.objects.filter(
            schedule=self.schedule,
            status='waitlist'
        ).order_by('booking_date').first()
        
        if waitlist_booking:
            waitlist_booking.status = 'confirmed'
            waitlist_booking.save()
