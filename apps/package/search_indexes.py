import datetime
from haystack.indexes import *
from haystack import site
from package.models import Package


class PackageIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
    total_members = IntegerField(null = False) 
       
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Package.objects.all()
        
    #def get_updated_field(self):
    #    return 'updated'
   
    def prepare_total_members(self, obj):
        return obj.userpackage_set.count()   
   
site.register(Package, PackageIndex)

