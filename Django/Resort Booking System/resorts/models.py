from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
import base64
from cryptography.fernet import Fernet
from django.conf import settings

def get_encryption_key():
    # Derive a 32-byte key from Django's SECRET_KEY for Fernet
    return base64.urlsafe_b64encode(settings.SECRET_KEY[:32].ljust(32, '0').encode())

def encrypt_data(data):
    if not data: return None
    f = Fernet(get_encryption_key())
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    if not encrypted_data: return None
    try:
        f = Fernet(get_encryption_key())
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception:
        # Fallback for plain text OTPs already in database
        return encrypted_data

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def is_admin(self):
        return self.role == 'admin'

class Resort(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    CATEGORY_CHOICES = (
        ('Beach', 'Beach'),
        ('Mountain', 'Mountain'),
        ('Urban', 'Urban'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Beach')
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # Admin can deactivate
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_resorts', null=True, blank=True)
    ar_model = models.FileField(upload_to='resort_ar_models/', blank=True, null=True)

    @property
    def report_count(self):
        return self.reports.count()

    @property
    def total_available_rooms(self):
        return sum(room.available_rooms for room in self.rooms.all())

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 5.0

    @property
    def min_price(self):
        min_p = self.rooms.aggregate(models.Min('price'))['price__min']
        return int(min_p) if min_p else 0

    def __str__(self):
        return self.name

class ResortReport(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.resort.name} by {self.user.username}"

class Room(models.Model):
    ROOM_TYPES = (
        ('Standard', 'Standard'),
        ('Deluxe', 'Deluxe'),
        ('Suite', 'Suite'),
    )
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField(default=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField() # Keeping for backward compatibility but will use logic for availability
    ar_model = models.FileField(upload_to='ar_models/', blank=True, null=True)

    def __str__(self):
        return f"{self.resort.name} - {self.room_type}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
        ('Checked-In', 'Checked-In'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    otp = models.CharField(max_length=255, blank=True, null=True) # Increased to store encrypted string
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_otp(self):
        plain_otp = ''.join(random.choices(string.digits, k=6))
        self.otp = encrypt_data(plain_otp)
        self.save()

    @property
    def decrypted_otp(self):
        return decrypt_data(self.otp)

    @property
    def resort(self):
        first_room = self.booked_rooms.first()
        return first_room.room.resort if first_room else None

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} ({self.status})"

class BookingRoom(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.room.room_type} in Booking {self.booking.id}"
class ResortReview(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.resort.name} by {self.user.username}"
