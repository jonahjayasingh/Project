from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('hod', 'HOD'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Domain(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_domains', limit_choices_to={'role': 'mentor'})
    mentors = models.ManyToManyField(User, related_name='allocated_domains', limit_choices_to={'role': 'mentor'}, blank=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('MENTOR_APPROVED', 'Mentor Approved'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    preferred_domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolled_students')
    domain_joined_at = models.DateTimeField(null=True, blank=True)
    assigned_mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_students', limit_choices_to={'role': 'mentor'})
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approval_remark = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Gamification
    points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username

class Resource(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    youtube_link = models.URLField()

    def __str__(self):
        return self.title

class Assignment(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title

class AssignmentStatus(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    completed = models.BooleanField(default=False)
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True)
    mentor_score = models.IntegerField(null=True, blank=True)
    mentor_feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'assignment')

class Quiz(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])

    def __str__(self):
        return f"{self.domain.name} - {self.question[:50]}"

class QuizResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    score = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.score}"

class PlacementResource(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField()
    company_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title

class Alumni(models.Model):
    name = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    current_company = models.CharField(max_length=200)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    profile_description = models.TextField()

    def __str__(self):
        return self.name

class Post(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name='alumni_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    certificate_file = models.FileField(upload_to='certificates/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Like(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('achievement', 'user')

class Comment(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_given', limit_choices_to={'role': 'student'})
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_received', limit_choices_to={'role': 'mentor'})
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
