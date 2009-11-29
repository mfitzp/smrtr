from django import forms
from django.contrib.admin import widgets        
# Spenglr                               
from spenglr.education.models import UserNetwork

class UserNetworkRegisterForm(forms.ModelForm):
    class Meta:
        model = UserNetwork
    def __init__(self, *args, **kwargs):
        super(UserNetworkRegisterForm, self).__init__(*args, **kwargs)
