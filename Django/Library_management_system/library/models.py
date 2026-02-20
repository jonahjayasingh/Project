from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Student(models.Model):
    """Student model with auto-generated student number"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_number = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50, verbose_name="Class")
    date_created = models.DateTimeField(auto_now_add=True)
    max_books_allowed = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.student_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.student_number:
            # Generate unique student number: STU + UUID (first 8 chars)
            self.student_number = f"STU{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_borrowed_books_count(self):
        """Get count of currently borrowed books"""
        return self.borrow_records.filter(status__in=['borrowed', 'overdue']).count()
    
    def get_pending_requests_count(self):
        """Get count of pending book requests"""
        return self.borrow_records.filter(status='pending').count()
    
    def can_borrow_more_books(self):
        """Check if student can borrow more books (including pending requests)"""
        active_count = self.get_borrowed_books_count() + self.get_pending_requests_count()
        return active_count < self.max_books_allowed



class Book(models.Model):
    """Book model with inventory tracking"""
    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('reference', 'Reference'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        # Ensure available copies don't exceed total copies
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0


class BorrowRecord(models.Model):
    """Borrow record tracking book loans and requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    request_date = models.DateTimeField(default=timezone.now)
    requested_days = models.IntegerField(default=14, help_text="Number of days requested to borrow")
    borrow_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Student's request notes")
    admin_notes = models.TextField(blank=True, help_text="Admin/Librarian notes")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.student.student_number} - {self.book.title} ({self.status})"
    
    def is_overdue(self):
        """Check if the book is overdue"""
        from django.utils import timezone
        if self.status == 'borrowed' and self.due_date:
            return timezone.now().date() > self.due_date
        return False
    
    def save(self, *args, **kwargs):
        # Update status to overdue if necessary
        if self.is_overdue() and self.status == 'borrowed':
            self.status = 'overdue'
        super().save(*args, **kwargs)
