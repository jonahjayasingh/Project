from django.db import models
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2

class Donation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Picked', 'Picked'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    )

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    food_type = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    cooked_time = models.DateTimeField(null=True, blank=True)
    expiry_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField()
    
    # Address and location fields
    address = models.TextField(help_text="Full pickup address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ngo_donations')
    assigned_volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteer_assignments')
    
    # Verification codes
    pickup_otp = models.CharField(max_length=6, blank=True, null=True)
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from datetime import timedelta
        if self.cooked_time and not self.expiry_time:
            self.expiry_time = self.cooked_time + timedelta(hours=6)
        
        if not self.pickup_otp:
            import random
            self.pickup_otp = str(random.randint(100000, 999999))
        if not self.delivery_otp:
            import random
            self.delivery_otp = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_type} - {self.donor.username}"
    
    def calculate_distance(self, target_lat, target_lon):
        """
        Calculate distance in kilometers from donation location to target location
        using Haversine formula
        """
        if not self.latitude or not self.longitude:
            return None
        
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1 = radians(float(self.latitude))
        lon1 = radians(float(self.longitude))
        lat2 = radians(float(target_lat))
        lon2 = radians(float(target_lon))
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return round(distance, 2)

class DonationRejection(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='rejections')
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rejected_donations')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('donation', 'ngo')

    def __str__(self):
        return f"Rejection: {self.donation} by {self.ngo.username}"
