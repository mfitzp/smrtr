from django.conf.urls.defaults import *
# Spenglr
from education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',


    # Module instance
    # url(r'^ci(?P<coursei_id>\d+)/$', 'education.views.coursei_detail',  name='coursei-detail'  ),

    # Module instance 
    # url(r'^mi(?P<modulei_id>\d+)/$', 'education.views.modulei_detail',  name='modulei-detail'  ),

    # Module generic
    url(r'^m(?P<module_id>\d+)/$', 'education.views.module_detail',  name='module-detail'  ),
    url(r'^m(?P<module_id>\d+)/providers/$', 'education.views.module_detail_providers',  name='module-detail-providers'  ),
    url(r'^m(?P<module_id>\d+)/register/$', 'education.views.module_register',  name='module-register'  ),
    
    # Concept generic
    url(r'^c(?P<concept_id>\d+)/$', 'education.views.concept_detail',  name='concept-detail'  ),
    url(r'^c(?P<concept_id>\d+)/register/$', 'education.views.concept_register',  name='concept-register'  ),

    # User specific pass module instance data
    url(r'^c(?P<concept_id>\d+)/exam/$', 'education.views.concept_exam', name='concept-exam' ),
    url(r'^c(?P<concept_id>\d+)/exam/submit$', 'education.views.concept_exam_submit', name='concept-exam-submit'),
    
    url(r'^c(?P<concept_id>\d+)/resources$', 'education.views.concept_resources', name='concept-resources' ),
    # url(r'^mi(?P<modulei_id>\d+)$', 'resources.views.module_userresources', name='resource-modulei-userresources' ),


    url(r'^c(?P<concept_id>\d+)/questions/add/', 'education.views.concept_add_questions', name='concept-add-questions' ),

)
