from django.conf.urls.defaults import *
# Smrtr
from questions.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

     url(r'^(?P<question_id>\d+)/$', 'questions.views.question_detail', name='question-detail' ),

     url(r'^tag/(?P<tag_id>\d+)/$', 'questions.views.questions_tagged', name='questions-tagged' ),


     url(r'^all$', 'django.views.generic.date_based.archive_index', { 'queryset': Question.objects.all(), 'date_field': 'updated' }, name='latest-questions' ),
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', { 'queryset': Question.objects.all() } ),

     # Non-user specific (no need for instance data)
     url(r'^c(?P<concept_id>\d+)/latest', 'questions.views.latest_questions_challenge', name='latest-questions-concept' ),


)
