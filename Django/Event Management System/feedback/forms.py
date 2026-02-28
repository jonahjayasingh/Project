from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select p-3 rounded-3 bg-light border-0 shadow-sm'}, choices=[(i, f"{i} Stars") for i in range(5, 0, -1)]),
            'comment': forms.Textarea(attrs={'class': 'form-control p-3 rounded-4 bg-light border-0 shadow-sm', 'rows': 4, 'placeholder': 'Share your experience with us...'}),
        }
