from django.conf.urls.defaults import *
# Spenglr
from network.models import *
from network.forms import *

# External
from haystack.views import *
from haystack.query import SearchQuerySet

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    #url(r'^all$', 'django.views.generic.list_detail.object_list', { 'queryset': Network.objects.all(), 'paginate_by': 25, 'template_name':'network_list.html' }, name='network-list'   ),

    url(r'^(?P<network_id>\d+)/$', 'network.views.network_detail', name='network-detail'  ),
    url(r'^(?P<network_id>\d+)/register/$', 'network.views.network_register', name='network-register'  ),
    url(r'^(?P<network_id>\d+)/members/$', 'network.views.network_members', name='network-members'  ),
    
    #url(r'^search/$', SearchView(form_class=NetworkSearchForm, template='network_search.html', searchqueryset=SearchQuerySet().models(Network)), name='network-search'),
    

    url(r'^search/$', 'network.views.network_search', name='network-search' ),    
    

)
