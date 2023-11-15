from django import forms
from .models import UserProfile

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'password', 'confirmpassword' , 'nid', 'date_of_birth', 'phone', 'division', 'district', 'upazila', 'profile_image']