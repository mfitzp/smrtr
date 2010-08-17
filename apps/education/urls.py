from django.conf.urls.defaults import *
# Smrtr
from education.models import *
from education.forms import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Topic instance
    # url(r'^ci(?P<coursei_id>\d+)/$', 'education.views.coursei_detail',  name='coursei-detail'  ),

    # Topic instance 
    # url(r'^mi(?P<topici_id>\d+)/$', 'education.views.topici_detail',  name='topici-detail'  ),

    # Topic generic
    url(r'^topic/(?P<topic_id>\d+)/$', 'education.views.topic_detail',  name='topic-detail'  ),
    url(r'^topic/(?P<topic_id>\d+)/providers/$', 'education.views.topic_providers',  name='topic-providers'  ),
    url(r'^topic/(?P<topic_id>\d+)/register/$', 'education.views.topic_register',  name='topic-register'  ),

    # Topic creation and editing
    url(r'^topic/create/$', 'education.views.topic_create',  name='topic-create'  ),
    url(r'^topic/(?P<topic_id>\d+)/edit/$', 'education.views.topic_edit',  name='topic-edit'  ),
    url(r'^topic/(?P<topic_id>\d+)/concepts/add/$', 'education.views.topic_detail',  name='topic-add-concepts'  ),

    url(r'^topic/search/$', 'education.views.topic_search',  name='topic-search'  ),


    # Concept generic
    url(r'^concept/(?P<concept_id>\d+)/$', 'education.views.concept_detail',  name='concept-detail'  ),
    url(r'^concept/(?P<concept_id>\d+)/register/$', 'education.views.concept_register',  name='concept-register'  ),
    url(r'^concept/(?P<concept_id>\d+)/providers/$', 'education.views.concept_providers',  name='concept-providers'  ),

    # Concept creation and editing
    url(r'^concept/create/$', 'education.views.concept_create',  name='concept-create'  ),
    url(r'^concept/(?P<concept_id>\d+)/edit/$', 'education.views.concept_edit',  name='concept-edit'  ),


    url(r'^concept/(?P<concept_id>\d+)/resources/$', 'education.views.concept_resources', name='concept-resources' ),


    url(r'^concept/(?P<concept_id>\d+)/questions/add/', 'education.views.concept_add_questions', name='concept-add-questions' ),
    url(r'^concept/(?P<concept_id>\d+)/resources/add/', 'education.views.concept_add_resources', name='concept-add-resources' ),

)
