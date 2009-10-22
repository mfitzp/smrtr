from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^n/$', 'django.views.generic.list_detail.object_list', { 'queryset': Network.objects.all(), 'paginate_by': 25 }, name='network-list'   ),
    url(r'^n/(?P<network_id>\d+)/$', 'spenglr.education.views.network_detail', name='network-detail'  ),
    url(r'^n/(?P<network_id>\d+)/register/$', 'spenglr.education.views.network_register', name='network-register'  ),

    url(r'^c/(?P<course_id>\d+)/$', 'spenglr.education.views.course_detail',  name='course-detail'  ),
    url(r'^c/(?P<course_id>\d+)/register/$', 'spenglr.education.views.course_register',  name='course-register'  ),

    url(r'^c/(?P<course_id>\d+)/(?P<module_id>\d+)/$', 'spenglr.education.views.module_detail',  name='module-detail'  ),

 
)
