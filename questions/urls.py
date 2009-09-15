from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

     (r'^m/(?P<object_id>\d+)$', 'django.views.generic.list_detail.object_detail', { 'queryset': Module.objects.all(), 'template_name': 'education/module_questions.html' }  ),

)
