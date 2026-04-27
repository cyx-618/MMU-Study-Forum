from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback, User_profile, Major

class UserRegisterForm(UserCreationForm):
   email=forms.EmailField()
   
   class Meta:
       model=User
       fields=['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):
   major= forms.ModelChoiceField(
       queryset=Major.objects.all(), 
       required=True,
       empty_label="-- Please Select Your Major --",
       label="Your Major"
       )
   class Meta:
       model=User_profile
       fields=['major','bio','profile_picture']
       labels={
          'bio':'Write your bio',
          'profile_picture':'Select Profile'
      }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the subject of your feedback'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your feedback here', 'rows': 5}),
        }
        labels = {
            'subject': 'Subject',
            'message': 'Message',
        }
