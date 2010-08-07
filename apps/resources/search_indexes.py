import datetime
from haystack.indexes import *
from haystack import site
from resources.models import Resource


class ResourceIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Resource.objects.all()


site.register(Resource, ResourceIndex)
