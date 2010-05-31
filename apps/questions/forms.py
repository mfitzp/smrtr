from django import forms
from django.contrib.admin import widgets                                       
# External
from haystack.forms import SearchForm

class QuestionSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(QuestionSearchForm, self).__init__(*args, **kwargs)