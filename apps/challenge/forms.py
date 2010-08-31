from django import forms
from django.contrib.admin import widgets                                       
# Smrtr
from network.models import Network
from challenge.models import Challenge
# External
from haystack.forms import SearchForm


class ChallengeForm(forms.ModelForm):

    class Meta:
        model = Challenge
        fields = ['name', 'description','image']
        
    def __init__(self, request, *args, **kwargs):
        super(ChallengeForm, self).__init__(*args, **kwargs)
        #if request: # If passed only show networks the user is on
            #self.fields['network'].queryset = Network.objects.filter(usernetwork__user=request.user)         


class ChallengeSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(ChallengeSearchForm, self).__init__(*args, **kwargs)
