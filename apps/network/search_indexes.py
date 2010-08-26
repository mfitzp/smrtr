import datetime
from haystack.indexes import *
from haystack import site
from network.models import Network


class NetworkIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
    
    type = IntegerField(model_attr='type', null = True) #type of network
    stage = IntegerField(model_attr='stage', null = True) #stage of network
    total_members = IntegerField(null = False) 
       
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Network.objects.all()#.filter(pub_date__lte=datetime.datetime.now())

    def get_updated_field(self):
        return 'updated'
        
    def prepare_total_members(self, obj):
        return obj.usernetwork_set.count()

site.register(Network, NetworkIndex)
