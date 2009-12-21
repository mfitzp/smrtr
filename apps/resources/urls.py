from django.conf.urls.defaults import *
# Spenglr
from resources.models import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

        url(r'^tag/(?P<tag_id>\d+)/$', 'resources.views.resources_tagged', name='resources-tagged' ),

        url(r'^all$', 'django.views.generic.date_based.archive_index', { 'queryset': Resource.objects.all(), 'date_field': 'created' }, name='latest-resources' ),

        url(r'^(?P<resource_id>\d+)/$', 'resources.views.resource_detail', name='resource-detail' ),

        url(r'^mi(?P<modulei_id>\d+)$', 'resources.views.module_userresources', name='resource-modulei-userresources' ),
)
