# post/forms.py
from django import forms
from .models import Post
from .models import Report

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'pdf', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Write your title here...',
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your questions here...',
                'rows': 10,
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Title', 
            'content': 'Content',
            'category': 'Category',
            'image': 'Image',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide more details about why you are reporting this post...'
            }),
        }
        labels = {
            'reason': 'Reason for Reporting',
            'description': 'Additional Details (Optional)',
        }