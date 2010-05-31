from django import forms
from django.contrib.admin import widgets        
# Spenglr                               
from network.models import *
# External
from countries.models import Country
from haystack.forms import SearchForm

class UserNetworkRegisterForm(forms.ModelForm):
    class Meta:
        model = UserNetwork
    def __init__(self, *args, **kwargs):
        super(UserNetworkRegisterForm, self).__init__(*args, **kwargs)

class NetworkSearchForm(SearchForm):

    type = forms.IntegerField(initial=None,required=False,widget=forms.Select(choices=TYPE_CHOICES))
    stage = forms.IntegerField(initial=None,required=False,widget=forms.Select(choices=STAGE_CHOICES))
    #country = forms.ModelMultipleChoiceField(initial=None,required=False,queryset=Country.objects.all())


    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(NetworkSearchForm, self).search()
        
        if self.cleaned_data['type']:
           sqs = sqs.filter(type=self.cleaned_data['type'])

        if self.cleaned_data['stage']:
            sqs = sqs.filter(stage=self.cleaned_data['stage'])

        # Check to see if a country was chosen.
        #if self.cleaned_data['country']:
        #   sqs = sqs.filter(country=self.cleaned_data['country'])

        return sqs


    def __init__(self, *args, **kwargs):
        super(NetworkSearchForm, self).__init__(*args, **kwargs)
       