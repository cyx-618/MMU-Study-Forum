from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback, User_profile, Major
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from .models import ProfileOTP

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
       label="Your Major",
       widget=forms.Select(attrs={
            'class': 'form-select',
           
        })
       )
   class Meta:
       model=User_profile
       fields=['major','bio','profile_picture']
       labels={
          'bio':'Write your bio',
          'profile_picture':'Select Profile'
      }
       
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.fields['major'].widget.attrs.update({
            'class': 'form-select',
            'data-placeholder': 'Select your major'
        })
        self.fields['major'].label = ""
        self.fields['bio'].label = ""
        self.fields['profile_picture'].widget = forms.FileInput()
        self.fields['profile_picture'].label = ""
        self.fields['profile_picture'].help_text = ""
        self.fields['bio'].help_text = ""
       
        self.helper.layout = Layout(
            Field('major', css_class='major-select form-control'),
            Field('bio', css_class='bio form-control', placeholder='Tell us about yourself!'),
            Field('profile_picture', css_class='profile-picture form-control-file'),
            Submit('submit', 'Update Profile', css_class='update-btn'),
        )
    

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('subject',label="Subject",css_class='subject form-contol'),
            Field('message', label="Message", css_class='message form-control '),
            Submit('submit', 'Submit', css_class='submit-btn'),
        )

class RequestOTPForm(forms.Form):
    email = forms.EmailField(label="Student Email",
            widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your student email...',
            'class': 'my-custom-input-class'  
        }))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@student.mmu.edu.my'): 
           raise forms.ValidationError("Please enter valid MMU email address")
        
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user found with this email address.")
        return email
    
class ResetPasswordForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter 6-Digit OTP",
        widget=forms.TextInput(attrs={
            'class':'my-custom-input-class'
        }))
    new_password = forms.CharField( label="Enter New Password",
                    widget=forms.PasswordInput(attrs={
                        'class':'my-custom-input-class'
                    }))
    confirm_password = forms.CharField(label="Confirm New Password",
                      widget=forms.PasswordInput(attrs={
                        'class':'my-custom-input-class'
                    }))

    def clean(self):
        cleaned_data = super().clean()
        otp_input = cleaned_data.get("otp")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        if otp_input:
          otp_exists = ProfileOTP.objects.filter(otp=otp_input).exists()
        
        if not otp_exists:
            raise forms.ValidationError("Invalid OTP. Please try again.")
        return cleaned_data
        