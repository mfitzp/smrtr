from django import forms
from django.contrib.admin import widgets        
from django.contrib.auth.models import User                               
# Smrtr
from discuss.models import *


class ThreadForm(forms.ModelForm):

    class Meta:
        model = Thread
        fields = ['title', 'tags']

    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        


