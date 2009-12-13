from django.conf.urls.defaults import *
# Spenglr
from education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^all$', 'django.views.generic.list_detail.object_list', { 'queryset': Network.objects.all(), 'paginate_by': 25, 'template_name':'network_list.html' }, name='network-list'   ),

    url(r'^(?P<network_id>\d+)/$', 'network.views.network_detail', name='network-detail'  ),
    url(r'^(?P<network_id>\d+)/register/$', 'network.views.network_register', name='network-register'  ),

)
