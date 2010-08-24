import datetime
from haystack.indexes import *
from haystack import site
from challenge.models import Challenge


class ChallengeIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Challenge.objects.all()
        
    def get_updated_field(self):
        return 'updated'
   
site.register(Challenge, ChallengeIndex)

