from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter post title...'}),
            'content': forms.Textarea(attrs={'placeholder': 'Write your story here... (Bullying detection active)'}),
        }
