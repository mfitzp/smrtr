from django import forms
from django.contrib.admin import widgets                                       
# Spenglr
from challenge.models import *
from education.models import *
# External
# from haystack.forms import SearchForm


class ChallengeForm(forms.ModelForm):

    description = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'textarea'}))

    class Meta:
        model = Challenge
        fields = ['name', 'description', 'concepts','total_questions']

    def __init__(self, request, *args, **kwargs):
        super(ChallengeForm, self).__init__(*args, **kwargs)    
        if request:
            self.fields['concepts'] = forms.ModelMultipleChoiceField(label='Concepts',queryset=Concept.objects.filter(userconcept__user=request.user)) # Only networks the user is on
