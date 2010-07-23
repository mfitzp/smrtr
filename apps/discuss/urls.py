from django.conf.urls.defaults import *
# Spenglr

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^(?P<forum_id>\d+)/$', 'discuss.views.forum', name='discuss_forum' ),
    url(r'^(?P<forum_id>\d+)/newthread/$', 'discuss.views.newthread', name='discuss_newthread' ),

    url(r'^thread/(?P<thread_id>\d+)/$', 'discuss.views.thread', name='discuss_thread' ),
    url(r'^thread/(?P<thread_id>\d+)/reply/$', 'discuss.views.reply', name='discuss_reply' ),
 
)

