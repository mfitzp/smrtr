from django import forms
from django.contrib.admin import widgets                                       
# Spenglr
from education.models import UserModule
# External
from haystack.forms import SearchForm

class UserModuleRegisterForm(forms.ModelForm):
    class Meta:
        model = UserModule
    def __init__(self, *args, **kwargs):
        super(UserModuleRegisterForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = widgets.AdminDateWidget()
    start_date = forms.DateField(required=True)


       