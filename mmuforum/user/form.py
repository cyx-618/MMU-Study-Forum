from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import User_profile

class UserRegisterForm(UserCreationForm):
  email=forms.EmailField()

  class Meta:
    model=User
    fields=['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):
  class Meta:
      model=User_profile
      fields=['major','bio','profile_picture']
      labels={
         'major':'Your Faculty:',
         'bio':'Write your bio',
         'profile_picture':'Select Profile'
      }
