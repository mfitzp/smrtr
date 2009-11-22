from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Module generic
    url(r'^c(?P<course_id>\d+)/$', 'spenglr.education.views.course_detail',  name='course-detail'  ),
    url(r'^c(?P<course_id>\d+)/providers$', 'spenglr.education.views.course_detail_providers',  name='course-detail-providers'  ),

    # Module instance
    url(r'^ci(?P<coursei_id>\d+)/$', 'spenglr.education.views.coursei_detail',  name='coursei-detail'  ),
    url(r'^ci(?P<coursei_id>\d+)/register/$', 'spenglr.education.views.coursei_register',  name='coursei-register'  ),

    # Module generic
    url(r'^m(?P<module_id>\d+)/$', 'spenglr.education.views.module_detail',  name='module-detail'  ),

    # Module instance 
    url(r'^mi(?P<modulei_id>\d+)/$', 'spenglr.education.views.modulei_detail',  name='modulei-detail'  ),
    url(r'^mi(?P<modulei_id>\d+)/register/ci(?P<coursei_id>\d+)/$', 'spenglr.education.views.modulei_register',  name='modulei-register'  ),

)
