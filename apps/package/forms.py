from django import forms
from django.contrib.admin import widgets                                       
# Smrtr
from network.models import Network
from package.models import Package
from challenge.models import Challenge
# External
from haystack.forms import SearchForm


class PackageForm(forms.ModelForm):

    class Meta:
        model = Package
        fields = ['name', 'description', 'image', 'network', 'challenges']

    def __init__(self, request, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)    
        if request: # If passed only show networks the user is on
            self.fields['network'].queryset = Network.objects.filter(usernetwork__user=request.user) 
            self.fields['challenges'].queryset = Challenge.objects.filter(userchallenge__user=request.user) 

  
class PackageSearchForm(SearchForm):

    def search(self):
        sqs = super(PackageSearchForm, self).search()
        sqs = sqs.order_by('-total_members','-type','score')        
        return sqs
        

    def __init__(self, *args, **kwargs):
        super(PackageSearchForm, self).__init__(*args, **kwargs)
       
