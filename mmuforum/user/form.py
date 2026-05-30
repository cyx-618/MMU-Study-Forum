from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback, User_profile, Major
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm


class UserRegisterForm(UserCreationForm):
   email=forms.EmailField()
   
   class Meta:
       model=User
       fields=['username','email','password1','password2']
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.fields['username'].label = ""
        self.fields['email'].label = ""
        self.fields['password1'].label = ""
        self.fields['password2'].label = ""
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = mark_safe(
            """
           <li> Password must be at least <strong>8 characters</strong> long.</li><br>
           <li>Password cannot be entirely numeric.</li>
            """,      
        )
        self.fields['password2'].help_text = ""
        
        self.helper.layout = Layout(
            Div(
                HTML('<i class="fa-solid fa-user field-icon"></i>'),
                Field('username', placeholder='Username', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper'
            ),
            Div(
                HTML('<i class="fa-solid fa-envelope field-icon"></i>'),
                Field('email', placeholder='School Email', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper'
            ),
            Div(
                HTML('<i class="fa-solid fa-lock field-icon"></i>'),
                Field('password1', placeholder='Password', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper password1'
            ),
            Div(
                HTML('<i class="fa-solid fa-lock field-icon"></i>'),
                Field('password2', placeholder='Confirm Password', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper'
            ),
            Submit('submit', 'Register', css_class='signup-btn')
        )
   def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        email = cleaned_data.get("email")
        if email and not email.endswith('@student.mmu.edu.my'):
            self.add_error('email', "Please enter a valid school email address.")
        if p1 and p2 and p1 != p2:
           if 'password2' in self._errors:
                del self._errors['password2']
           raise forms.ValidationError("The two password fields didn't match.")
        
        return cleaned_data
   
class LoginForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.error_messages['invalid_login'] = "Invalid username or password."
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.show_errors = False

        self.fields['username'].label = ""
        self.fields['password'].label = ""
        self.fields['username'].help_text = ""
        self.fields['password'].help_text = ""

        self.helper.layout = Layout(
            Div(
                HTML('<i class="fa-solid fa-user field-icon"></i>'),
                Field('username', placeholder='Username', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper'
            ),
            Div(
                HTML('<i class="fa-solid fa-lock field-icon"></i>'),
                Field('password', placeholder='Password', css_class='my-custom-input-class'),
                css_class='input-icon-wrapper'
            ),
               
        )

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
