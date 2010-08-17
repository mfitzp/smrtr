import datetime
from haystack.indexes import *
from haystack import site
from education.models import Topic, Concept


class TopicIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Topic.objects.all()
        
    def get_updated_field(self):
        return 'updated'
        
class ConceptIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Concept.objects.all()        

    def get_updated_field(self):
        return 'updated'

site.register(Topic, TopicIndex)
site.register(Concept, ConceptIndex)
