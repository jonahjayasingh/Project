from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, Domain, Resource, Assignment, AssignmentStatus, Quiz, Achievement, Feedback, Alumni, Post, PlacementResource

class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['preferred_domain']
        widgets = {
            'preferred_domain': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'preferred_domain': 'Choose Your Learning Domain',
        }

class DomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'youtube_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'youtube_link': forms.URLInput(attrs={'class': 'form-control'}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentStatus
        fields = ['submission_file']
        widgets = {
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentStatus
        fields = ['mentor_score', 'mentor_feedback']
        widgets = {
            'mentor_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'mentor_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['question', 'option1', 'option2', 'option3', 'option4', 'correct_answer']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'option1': forms.TextInput(attrs={'class': 'form-control'}),
            'option2': forms.TextInput(attrs={'class': 'form-control'}),
            'option3': forms.TextInput(attrs={'class': 'form-control'}),
            'option4': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.Select(attrs={'class': 'form-select'}),
        }

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'certificate_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['mentor', 'domain', 'rating', 'comment']
        widgets = {
            'mentor': forms.Select(attrs={'class': 'form-select'}),
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
