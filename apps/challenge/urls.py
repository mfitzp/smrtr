from django.conf.urls.defaults import *
# Spenglr
from education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Create new challenge: pass definition parameters on query-string
    # concept_ids, module_ids, home_network, privacy
    # Pass skip_config=true to bypass editing (useful for quick personal challenges: note user can invite another user at any time)    
    url(r'^create/$', 'challenge.views.edit', name='challenge-create' ),

    url(r'^(?P<challenge_id>\d+)/$', 'challenge.views.detail', name='challenge-detail' ),
    url(r'^(?P<challenge_id>\d+)/edit/$', 'challenge.views.edit', name='challenge-edit' ),

    url(r'^(?P<challenge_id>\d+)/do/$', 'challenge.views.do', name='challenge-do' ),
    url(r'^(?P<challenge_id>\d+)/do/submit/$', 'challenge.views.do_submit', name='challenge-do-submit'),
    
 
)
