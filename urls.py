from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

def i18n_javascript(request):
  return admin.site.i18n_javascript(request)

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:

    (r'^admin/jsi18n', i18n_javascript),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^$', 'core.views.home', name='home'),

    (r'^comments/', include('django.contrib.comments.urls')),

    #(r'^login/$', 'spenglr.core.views.loginhandler'),
    #(r'^logout/$', 'spenglr.core.views.logouthandler'),

    (r'^network/', include('network.urls')),
    (r'^education/', include('education.urls')),
    (r'^resources/', include('resources.urls')),    
    (r'^challenge/', include('challenge.urls')),

    (r'^accounts/intro/$', 'core.views.intro'),
    (r'^accounts/', include('registration.urls')),

    (r'^profile/', include('profiles.urls')),
    (r'^welcome/', include('welcome.urls')),

    (r'^questions/', include('questions.urls')),

    (r'^notification/', include('notification.urls')),

    url(r'^wall/(?P<slug>[-\w]+)/$', 'core.views.wall_home', name="wall_home"),
    url(r'^wall/add/(?P<slug>[-\w]+)/$', 'core.views.wall_add', name="add_wall_item"),
    #url(r'^wall/edit/(?P<id>\d+)/$', 'core.views.wall_edit', name="edit_wall_item"),
    
    (r'^search/', include('haystack.urls')),
    
    (r'^avatar/', include('avatar.urls')),
    
    (r'^messages/', include('messages.urls')),
)

