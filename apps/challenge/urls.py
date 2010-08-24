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
    url(r'^(?P<challenge_id>\d+)/providers/$', 'challenge.views.providers',  name='challenge-providers'  ),
    url(r'^(?P<challenge_id>\d+)/register/$', 'challenge.views.register',  name='challenge-register'  ),

    # Challenge creation and editing
    url(r'^create/$', 'challenge.views.create',  name='challenge-create'  ),
    url(r'^(?P<challenge_id>\d+)/edit/$', 'challenge.views.edit',  name='challenge-edit'  ),
    url(r'^(?P<challenge_id>\d+)/concepts/add/$', 'challenge.views.detail',  name='challenge-add-concepts'  ),

    url(r'^search/$', 'challenge.views.search',  name='challenge-search'  ),


    url(r'^(?P<challenge_id>\d+)/prepare/$', 'challenge.views.prepare', name='challenge-prepare' ),
    url(r'^(?P<challenge_id>\d+)/do/$', 'challenge.views.do', name='challenge-do' ),
    url(r'^(?P<challenge_id>\d+)/do/submit/$', 'challenge.views.do_submit', name='challenge-do-submit'),
    url(r'^(?P<challenge_id>\d+)/newset/$', 'challenge.views.newset', name='challenge-newset'),
    url(r'^(?P<challenge_id>\d+)/newset/ajax/$', 'challenge.views.newset_ajax', name='challenge-newset-ajax'),

)
