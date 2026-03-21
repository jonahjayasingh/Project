from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, FloatField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    type = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile", null=True, blank=True)
    admission_no = models.CharField(max_length=255, null=True, blank=True)
    registration_no = models.CharField(max_length=255, null=True, blank=True)
    branch = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    ten_th = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    twelve_th = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def calculate_cgpa(self):
        """Calculate CGPA based on semester SGPA and total credits."""
        sgpa_data = self.sgpa_records.annotate(
            weighted_sgpa=F('sgpa') * F('total_credits')
        ).aggregate(
            total_weighted=Sum('weighted_sgpa', output_field=FloatField()),
            total_credits=Sum('total_credits', output_field=FloatField())
        )
        total_weighted = sgpa_data['total_weighted'] or 0
        total_credits = sgpa_data['total_credits'] or 0

        if total_credits == 0:
            return None
        return round(total_weighted / total_credits, 2)

    def save(self, *args, **kwargs):
        # If no PK yet, skip CGPA calculation
        if self.pk:
            self.cgpa = self.calculate_cgpa()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} ({self.branch or 'No branch'})"



class StudentSGPA(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sgpa_records')
    semester = models.CharField(max_length=100)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    total_credits = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_sgpa(self):
        """Calculate SGPA = Σ(Credit × GradePoint) / Σ(Credits), skipping zero-credit subjects."""
        valid_subjects = self.subjects.filter(
            subject_credits__gt=0,
            grade_point__isnull=False
        )

        if not valid_subjects.exists():
            return None

        subject_data = valid_subjects.annotate(
            weighted_score=F('subject_credits') * F('grade_point')
        ).aggregate(
            total_weighted=Sum('weighted_score', output_field=FloatField()),
            total_credits=Sum('subject_credits', output_field=FloatField())
        )

        total_weighted = subject_data['total_weighted'] or 0
        total_credits = subject_data['total_credits'] or 0

        if total_credits == 0:
            return None

        return round(total_weighted / total_credits, 2)
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new object

        # First save to get a primary key if needed
        super().save(*args, **kwargs)

        # Now we can safely access related subjects
        subject_data = self.subjects.aggregate(
            total_credits=Sum('subject_credits', output_field=FloatField())
        )
        self.total_credits = subject_data.get('total_credits') or 0
        self.sgpa = self.calculate_sgpa()

        # Update the record again only if we have subjects
        super().save(update_fields=['total_credits', 'sgpa'])

        # Finally, update the student's CGPA
        self.student.save(update_fields=['cgpa'])


    def __str__(self):
        return f"{self.student.user.username} | Sem {self.semester}: {self.sgpa or 'N/A'}"



class Subject(models.Model):
    student_sgpa = models.ForeignKey(StudentSGPA, on_delete=models.CASCADE, related_name='subjects')
    subject_name = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=255)
    subject_credits = models.PositiveIntegerField()
    subject_grade = models.CharField(max_length=2, blank=True, null=True)
    grade_point = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Convert grade (A, B, etc.) to grade point automatically."""
        grade_mapping = {
            'S': 10.0,
            'A': 9.0,
            'B': 8.0,
            'C': 7.0,
            'D': 6.0,
            'E': 5.0,
            'F': 0.0,
        }
        if self.subject_grade:
            self.grade_point = grade_mapping.get(self.subject_grade.upper(), 0.0)
        super().save(*args, **kwargs)
        # Update SGPA when a subject changes
        self.student_sgpa.save()

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"




class Gallery(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="galary")
    image = models.ImageField(upload_to="galary")
    date = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=255,default="")
    gallery_type = models.CharField(max_length=255,default="")

    def __str__(self):
        return self.caption or f"Gallery {self.id}"

class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="gallery_images")

    def __str__(self):
        return f"Image for {self.gallery.caption}"

class Mcq(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="mcqs")
    mcq_title = models.CharField(max_length=255)
    mcq_duration = models.IntegerField()
    is_active = models.BooleanField(default=True)
    no_of_questions = models.IntegerField()
    date = models.DateTimeField(auto_now_add=False,blank=True,null=True)

    def __str__(self):
        return self.mcq_title
    



class Events(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="events")
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    event_type = models.CharField(max_length=255, blank=True, null=True)
    event_mcq = models.ForeignKey(
        Mcq, on_delete=models.CASCADE, null=True, blank=True, related_name="mcq_events"
    )
    event_location = models.CharField(max_length=255)
    event_description = models.TextField()
    event_image = models.ImageField(upload_to="events")




class EventRegister(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="event_registers")
    event = models.ForeignKey(Events,on_delete=models.CASCADE, related_name="event_registers")
    project_title = models.CharField(max_length=255, blank=True, null=True)
    project_description = models.TextField(blank=True, null=True)
    project_members = models.TextField(blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    mcq = models.ForeignKey(Mcq,on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    def get_options(self):
        return [self.option1, self.option2, self.option3, self.option4]
    
class Certificate(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="certificates")
    event = models.ForeignKey(Events,on_delete=models.CASCADE, related_name="certificates")
    cert_id = models.CharField(max_length=255, unique=True)
    passed = models.BooleanField(default=False)
    pdf = models.FileField(upload_to="certificates", null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="notifications")
    event = models.ForeignKey(Events,on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
