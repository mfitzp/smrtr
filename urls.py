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
    (r'^$', 'core.views.index'),

    #(r'^login/$', 'spenglr.core.views.loginhandler'),
    #(r'^logout/$', 'spenglr.core.views.logouthandler'),

    (r'^education/', include('education.urls')),
    (r'^network/', include('network.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^profile/', include('profile.urls')),

    (r'^questions/', include('questions.urls')),
    #(r'^resources/', include('spenglrcom.resources.urls')),

    (r'^notification/', include('notification.urls')),

    (r'^wall/', include('wall.urls')),

    (r'^avatar/', include('avatar.urls')),
)

