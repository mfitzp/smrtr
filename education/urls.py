from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    (r'^i/$', 'django.views.generic.list_detail.object_list', { 'queryset': Institution.objects.all() }  ),

    url(r'^i/(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Institution.objects.all() }, name='institution-detail'  ),
    url(r'^m/(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Module.objects.all() }, name='module-detail' ),
    url(r'^c/(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Course.objects.all() }, name='course-detail'  ),

)
