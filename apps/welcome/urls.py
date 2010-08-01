from django.conf.urls.defaults import *
# Smrtr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^1$', 'welcome.views.profile', name='welcome-1' ),
    url(r'^2$', 'network.views.search', {'next': 'home'}, name='welcome-2' )
    #url(r'^3$', 'welcome.views.profile', name='welcome-1' ),

)
