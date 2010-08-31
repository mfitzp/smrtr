from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
# Smrtr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^1$', 'welcome.views.profile', name='welcome-1' ),
    #url(r'^2$', 'network.views.search', {'next': '/'}, name='welcome-2' ),
    # Skip this so user gets the welcome message and instruction (keeps it easy to follow)
    url(r'^2$', 'package.views.search', {'next': '/'}, name='welcome-2' )

)
