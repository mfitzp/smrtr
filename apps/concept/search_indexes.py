import datetime
from haystack.indexes import *
from haystack import site
from concept.models import Concept


        
class ConceptIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Concept.objects.all()        

    def get_updated_field(self):
        return 'updated'

site.register(Concept, ConceptIndex)
