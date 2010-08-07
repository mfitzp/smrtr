from django import forms
from django.contrib.admin import widgets                                       
# External
from haystack.forms import SearchForm

class ResourceSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(ResourceSearchForm, self).__init__(*args, **kwargs)
