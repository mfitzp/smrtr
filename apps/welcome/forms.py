from django import forms
from django.contrib.admin import widgets        
from django.contrib.auth.models import User                               
# Smrtr
from profiles.models import *


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)


class ProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['about', 'city', 'state', 'country','avatar']
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)



