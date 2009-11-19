from django.conf.urls.defaults import *
from spenglr.education.models import *
from spenglr.questions.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

     url(r'^(?P<question_id>\d+)/$', 'spenglr.questions.views.question_detail', name='question-detail' ),

     url(r'^tag/(?P<tag_id>\d+)/$', 'spenglr.questions.views.questions_tagged', name='questions-tagged' ),


     url(r'^all$', 'django.views.generic.date_based.archive_index', { 'queryset': Question.objects.all(), 'date_field': 'last_updated'}, name='latest-questions' ),
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Question.objects.all() } ),

     # User specific pass module instance data
     url(r'^mi(?P<modulei_id>\d+)$', 'spenglr.questions.views.questions', name='question-modulei-exam' ),
     url(r'^mi(?P<modulei_id>\d+)/submit$', 'spenglr.questions.views.submit', name='question-modulei-submit'),

     # Non-user specific (no need for instance data)
     url(r'^m(?P<module_id>\d+)/latest', 'spenglr.questions.views.latest_questions_module', name='latest-questions-module' ),


)
