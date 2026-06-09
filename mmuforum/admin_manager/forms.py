from django import forms
from django.contrib.auth.models import User
from user.models import Major

class AdminProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}), required=False)
    major = forms.ModelChoiceField(queryset=Major.objects.all(), required=False, empty_label="Select a major")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}), required=False)
    is_active = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['bio'].initial = self.instance.user_profile.bio
            self.fields['major'].initial = self.instance.user_profile.major