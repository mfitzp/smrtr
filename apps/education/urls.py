from django.conf.urls.defaults import *
# Smrtr
from education.models import *
from education.forms import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',


    # Module instance
    # url(r'^ci(?P<coursei_id>\d+)/$', 'education.views.coursei_detail',  name='coursei-detail'  ),

    # Module instance 
    # url(r'^mi(?P<modulei_id>\d+)/$', 'education.views.modulei_detail',  name='modulei-detail'  ),

    # Module generic
    url(r'^module/(?P<module_id>\d+)/$', 'education.views.module_detail',  name='module-detail'  ),
    url(r'^module/(?P<module_id>\d+)/providers/$', 'education.views.module_providers',  name='module-providers'  ),
    url(r'^module/(?P<module_id>\d+)/register/$', 'education.views.module_register',  name='module-register'  ),

    # Module creation and editing
    url(r'^module/create/$', 'education.views.module_create',  name='module-create'  ),
    url(r'^module/(?P<module_id>\d+)/edit/$', 'education.views.module_edit',  name='module-edit'  ),
    url(r'^module/(?P<module_id>\d+)/concepts/add/$', 'education.views.module_detail',  name='module-add-concepts'  ),

    url(r'^module/search/$', 'education.views.module_search',  name='module-search'  ),


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
