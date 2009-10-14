from django.conf.urls.defaults import *
from spenglr.education.models import *
from spenglr.questions.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

     (r'^m/(?P<module_id>\d+)$', 'spenglr.questions.views.questions' ),
     url(r'^m/(?P<module_id>\d+)/submit$', 'spenglr.questions.views.submit', name='question-submit'),

     url(r'^all$', 'django.views.generic.date_based.archive_index', { 'queryset': Question.objects.all(), 'date_field': 'last_updated'}, name='latest-questions' ),
     url(r'^m/(?P<module_id>\d+)', 'spenglr.questions.views.latest_questions_module', name='latest-questions-module' ),
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Question.objects.all() } ),


)
