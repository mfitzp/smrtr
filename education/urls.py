from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^c/(?P<course_id>\d+)/$', 'spenglr.education.views.course_detail',  name='course-detail'  ),
    url(r'^c/(?P<course_id>\d+)/register/$', 'spenglr.education.views.course_register',  name='course-register'  ),

    url(r'^m/(?P<module_id>\d+)/$', 'spenglr.education.views.module_detail',  name='module-detail'  ),
 
)
