from django.conf.urls.defaults import *
# Spenglr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', 'profiles.views.profile', name='profile' ),
    url(r'^edit/$', 'profiles.views.edit_profile', name='profile-edit' ),
    url(r'^avatar/$', 'profiles.views.change_avatar', name='avatar-change' ),

    url(r'^(?P<user_id>\d+)/$', 'profiles.views.profile', name='user-profile' ),

)
