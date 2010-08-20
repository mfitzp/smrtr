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

    url(r'^(?P<network_id>\d+)/$', 'network.views.detail', name='network-detail'  ),
    url(r'^(?P<network_id>\d+)/register/$', 'network.views.register', name='network-register'  ),
    url(r'^(?P<network_id>\d+)/members/$', 'network.views.members', name='network-members'  ),
    url(r'^(?P<network_id>\d+)/homesweethome/$', 'network.views.set_home', name='network-set-home'  ),
    

    url(r'^search/$', 'network.views.search', name='network-search' ),    
    

)
