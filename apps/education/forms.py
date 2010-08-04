from django import forms
from django.contrib.admin import widgets                                       
# Smrtr
from network.models import Network
from education.models import Module, Concept
# External
from haystack.forms import SearchForm


class ModuleForm(forms.ModelForm):

    class Meta:
        model = Module
        fields = ['name', 'description', 'network', 'concepts']

    def __init__(self, request, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)    
        if request: # If passed only show networks the user is on
            self.fields['network'].queryset = Network.objects.filter(usernetwork__user=request.user) 
            self.fields['concepts'].queryset = Concept.objects.filter(userconcept__user=request.user) 


        
class ConceptForm(forms.ModelForm):

    class Meta:
        model = Concept
        fields = ['name', 'description', 'network']
        
    def __init__(self, request, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        if request: # If passed only show networks the user is on
            self.fields['network'].queryset = Network.objects.filter(usernetwork__user=request.user)         

