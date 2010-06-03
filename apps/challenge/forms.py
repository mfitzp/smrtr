from django import forms
from django.contrib.admin import widgets                                       
# Spenglr
from challenge.models import *
from education.models import *
# External
# from haystack.forms import SearchForm

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
    def __init__(self, *args, **kwargs):
        super(ChallengeForm, self).__init__(*args, **kwargs)
        
    name = forms.CharField(required=True)
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'textarea'}))
    concepts = forms.ModelMultipleChoiceField(label='Concepts covered',queryset=Concept.objects.all()) # Concepts to source questions from
    total_questions = forms.IntegerField(label='Max number of questions',required=False) # Number of questions
    minsq = forms.IntegerField(label='Min SQ',required=False) # Min SQ for questions
    maxsq = forms.IntegerField(label='Max SQ',required=False) # Max SQ for questions
       
