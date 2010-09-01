from django.conf.urls.defaults import *
# Smrtr
from challenge.models import *
from challenge.forms import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Challenge generic
    url(r'^(?P<challenge_id>\d+)/$', 'challenge.views.detail',  name='challenge-detail'  ),
    url(r'^(?P<challenge_id>\d+)/register/$', 'challenge.views.register',  name='challenge-register'  ),
    url(r'^(?P<challenge_id>\d+)/providers/$', 'challenge.views.providers',  name='challenge-providers'  ),

    # Challenge creation and editing
    url(r'^create/$', 'challenge.views.create',  name='challenge-create'  ),
    url(r'^(?P<challenge_id>\d+)/edit/$', 'challenge.views.edit',  name='challenge-edit'  ),
    url(r'^(?P<challenge_id>\d+)/resources/$', 'challenge.views.resources', name='challenge-resources' ),

    url(r'^search/$', 'challenge.views.search',  name='challenge-search'  ),
    
    url(r'^(?P<challenge_id>\d+)/questions/add/', 'challenge.views.add_questions', name='challenge-add-questions' ),
    url(r'^(?P<challenge_id>\d+)/resources/add/', 'challenge.views.add_resources', name='challenge-add-resources' ),

    url(r'^(?P<challenge_id>\d+)/prepare/$', 'challenge.views.prepare', name='challenge-prepare' ),
    url(r'^(?P<challenge_id>\d+)/do/$', 'challenge.views.do', name='challenge-do' ),
    url(r'^(?P<challenge_id>\d+)/do/submit/$', 'challenge.views.do_submit', name='challenge-do-submit'),

    #url(r'^next/$', 'challenge.views.next', name='challenge-next' ),

)
