# post/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image']
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
            'title': 'Title',  # 改变显示的文字
            'content': 'Content',
            'category': 'Category',
            'image': 'Image',
        }