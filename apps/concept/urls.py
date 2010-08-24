from django.conf.urls.defaults import *
# Smrtr
from concept.models import *
from concept.forms import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Concept generic
    url(r'^(?P<concept_id>\d+)/$', 'concept.views.detail',  name='concept-detail'  ),
    url(r'^(?P<concept_id>\d+)/register/$', 'concept.views.register',  name='concept-register'  ),
    url(r'^(?P<concept_id>\d+)/providers/$', 'concept.views.providers',  name='concept-providers'  ),

    # Concept creation and editing
    url(r'^create/$', 'concept.views.create',  name='concept-create'  ),
    url(r'^(?P<concept_id>\d+)/edit/$', 'concept.views.edit',  name='concept-edit'  ),
    url(r'^(?P<concept_id>\d+)/resources/$', 'concept.views.resources', name='concept-resources' ),


    url(r'^(?P<concept_id>\d+)/questions/add/', 'concept.views.add_questions', name='concept-add-questions' ),
    url(r'^(?P<concept_id>\d+)/resources/add/', 'concept.views.add_resources', name='concept-add-resources' ),

)
