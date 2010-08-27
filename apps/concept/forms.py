from django import forms
from django.contrib.admin import widgets                                       
# Smrtr
from network.models import Network
from concept.models import Concept
# External
from haystack.forms import SearchForm


class ConceptForm(forms.ModelForm):

    class Meta:
        model = Concept
        fields = ['name', 'description', 'network']
        
    def __init__(self, request, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        if request: # If passed only show networks the user is on
            self.fields['network'].queryset = Network.objects.filter(usernetwork__user=request.user)         


class ConceptSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(ConceptSearchForm, self).__init__(*args, **kwargs)
