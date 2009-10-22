from django import forms
from django.contrib.admin import widgets                                       
from spenglr.education.models import UserCourse

class UserNetworkRegisterForm(forms.ModelForm):
    class Meta:
        model = UserNetwork
    def __init__(self, *args, **kwargs):
        super(UserNetworkRegisterForm, self).__init__(*args, **kwargs)

class UserCourseRegisterForm(forms.ModelForm):
    class Meta:
        model = UserCourse
    def __init__(self, *args, **kwargs):
        super(UserCourseRegisterForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = widgets.AdminDateWidget()
    start_date = forms.DateField(required=True)

