from django.conf.urls.defaults import *
# Spenglr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^1$', 'welcome.views.profile', name='welcome-1' ),
    url(r'^2$', 'welcome.views.networks', name='welcome-2' ),

)
