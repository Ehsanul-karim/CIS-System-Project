from django import forms
from .models import UserProfile

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'password', 'confirmpassword' , 'nid', 'date_of_birth', 'phone', 'division', 'district', 'upazila', 'profile_image']


class FilterForm(forms.Form):
    anyfield = forms.BooleanField(required=False)
    firnumber = forms.BooleanField(required=False)
    victim_name = forms.BooleanField(required=False)
    submissiondate = forms.BooleanField(required=False)
    occurance_date = forms.BooleanField(required=False)
    crimeType = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)