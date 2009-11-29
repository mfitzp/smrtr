from django import forms
from django.contrib.admin import widgets                                       
# Spenglr
from education.models import UserCourse

class UserCourseRegisterForm(forms.ModelForm):
    class Meta:
        model = UserCourse
    def __init__(self, *args, **kwargs):
        super(UserCourseRegisterForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = widgets.AdminDateWidget()
    start_date = forms.DateField(required=True)

