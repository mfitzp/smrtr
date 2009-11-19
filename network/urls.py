from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^all$', 'django.views.generic.list_detail.object_list', { 'queryset': Network.objects.all(), 'paginate_by': 25 }, name='network-list'   ),

    url(r'^(?P<network_id>\d+)/$', 'spenglr.network.views.network_detail', name='network-detail'  ),
    url(r'^(?P<network_id>\d+)/register/$', 'spenglr.network.views.network_register', name='network-register'  ),

)
