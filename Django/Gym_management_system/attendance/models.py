from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    """
    Track member attendance (gym check-ins)
    """
    
    TYPE_CHOICES = (
        ('gym', 'Gym'),
        ('class', 'Class'),
    )
    
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    attendance_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='gym')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-check_in_time']
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.date} ({self.check_in_time.strftime('%H:%M')})"
    
    def duration(self):
        """Calculate duration of gym visit"""
        if self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return None
    
    def is_checked_out(self):
        """Check if member has checked out"""
        return self.check_out_time is not None
