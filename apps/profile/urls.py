from django.conf.urls.defaults import *
# Spenglr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^(?P<user_id>\d+)/$', 'profile.views.profile', name='user-profile' ),

)