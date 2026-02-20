from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=15)
    address = models.TextField()
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name

class LabAssistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_profile')
    lab_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Discovery fields
    city = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    bio = models.TextField(blank=True, help_text="Short description of the lab")
    
    # Capacity & Governance
    daily_capacity = models.PositiveIntegerField(default=50)
    is_emergency_closed = models.BooleanField(default=False)
    
    # Reputation
    rating_avg = models.FloatField(default=0.0)
    payment_qr_code = models.ImageField(upload_to='lab_qrs/', null=True, blank=True)

    def __str__(self):
        return f"{self.lab_name} ({self.user.username})"

class LabTechnician(models.Model):
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='technicians')
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.lab.lab_name}"

class LabTest(models.Model):
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='available_tests')
    test_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.test_name} ({self.lab.lab_name})"

class LabPackage(models.Model):
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='packages')
    package_name = models.CharField(max_length=255)
    description = models.TextField()
    tests = models.ManyToManyField(LabTest, related_name='included_in_packages')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.package_name} - {self.lab.lab_name}"

    @property
    def final_price(self):
        return self.price * (Decimal('1') - Decimal(str(self.discount_percentage)) / Decimal('100'))

class TestBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Confirmed', 'Confirmed'),
        ('Sample Collected', 'Sample Collected'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending Verification', 'Pending Verification'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    
    REFUND_STATUS_CHOICES = [
        ('Not Applicable', 'Not Applicable'),
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='bookings')
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    package = models.ForeignKey(LabPackage, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    
    test_name = models.CharField(max_length=255) # Kept for backward compatibility or manual entry
    booking_date = models.DateField()
    time_slot = models.TimeField(null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Approval')
    
    # Staff Assignment
    technician = models.ForeignKey(LabTechnician, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    internal_notes = models.TextField(blank=True, help_text="Visible only to lab staff")

    # Payment fields
    payment_proof = models.FileField(upload_to='payment_proofs/', null=True, blank=True)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending Verification')
    payment_rejection_reason = models.TextField(blank=True, null=True)
    refund_status = models.CharField(max_length=30, choices=REFUND_STATUS_CHOICES, default='Not Applicable')
    
    # Cancellation Policy
    cancellation_reason = models.TextField(blank=True, null=True)
    is_no_show = models.BooleanField(default=False)
    
    # Report fields
    report_file = models.FileField(upload_to='test_reports/', null=True, blank=True)
    report_remarks = models.TextField(blank=True, null=True)
    is_report_final = models.BooleanField(default=False)
    
    # Financial Record
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name} (#{self.id})"

class ReportVersion(models.Model):
    booking = models.ForeignKey(TestBooking, on_delete=models.CASCADE, related_name='versions')
    report_file = models.FileField(upload_to='test_reports/history/')
    version_number = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"V{self.version_number} - {self.booking.test_name}"

class LabReview(models.Model):
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField('TestBooking', on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    lab_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating} stars for {self.lab.lab_name} by {self.patient.full_name}"

class LabWorkingHours(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='working_hours')
    day = models.IntegerField(choices=DAYS)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('lab', 'day')

class LabHoliday(models.Model):
    lab = models.ForeignKey(LabAssistant, on_delete=models.CASCADE, related_name='holidays')
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('lab', 'date')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    NOTIFICATION_TYPES = [
        ('Booking', 'Booking Update'),
        ('Report', 'Report Ready'),
        ('General', 'Announcement'),
    ]
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='General')

    def __str__(self):
        return f"Notification for {self.user.username}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.key

class StaticPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
