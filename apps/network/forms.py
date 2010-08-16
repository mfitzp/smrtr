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

    #type = forms.IntegerField(initial=None,required=False,widget=forms.Select(choices=TYPE_CHOICES))
    #stage = forms.IntegerField(initial=None,required=False,widget=forms.Select(choices=STAGE_CHOICES))
    #country = forms.ModelMultipleChoiceField(initial=None,required=False,queryset=Country.objects.all())

    def search(self):
        sqs = super(NetworkSearchForm, self).search()
        return sqs
        
    def search_split(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(NetworkSearchForm, self).search()

        # TYPE_CHOICES defines the subtypes of network available
        # Listing order is reversed (puts Other last)        
        search = list()

        #search['all'] = sqs # Allow pure jumbled listing
        # Seperate the network types for listing
        for tid,tname in TYPE_CHOICES:
            item = dict()
            item['type'] = tid
            item['name'] = tname
            item['results'] = sqs.filter(type=tid)[0:10]
            search.insert(0, item) # Reverse

        return search        


    def __init__(self, *args, **kwargs):
        super(NetworkSearchForm, self).__init__(*args, **kwargs)
       
