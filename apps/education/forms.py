from django import forms
from django.contrib.admin import widgets                                       
# Smrtr
from network.models import Network
from education.models import Topic, Concept
# External
from haystack.forms import SearchForm


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ['name', 'description', 'network', 'concepts']

    def __init__(self, request, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)    
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


class TopicSearchForm(SearchForm):

    def search(self):
        sqs = super(TopicSearchForm, self).search()
        return sqs
        

    def __init__(self, *args, **kwargs):
        super(TopicSearchForm, self).__init__(*args, **kwargs)
       
