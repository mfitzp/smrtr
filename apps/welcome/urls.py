from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
# Smrtr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^1$', 'welcome.views.profile', name='welcome-1' ),
    url(r'^2$', 'network.views.search', {'next': '3'}, name='welcome-2' ),
    url(r'^3$', 'education.views.topic_search', {'next': '/'}, name='welcome-3' )

)
