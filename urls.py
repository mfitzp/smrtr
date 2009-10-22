from django.conf.urls.defaults import *
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
    (r'^$', 'spenglr.core.views.index'),
    #(r'^login/$', 'spenglr.core.views.loginhandler'),
    #(r'^logout/$', 'spenglr.core.views.logouthandler'),

    (r'^education/', include('spenglr.education.urls')),

    #(r'^network/', include('spenglr.network.urls')),
    
    (r'^accounts/', include('registration.urls')),

    # These exist so we can keep a standardised url forum across all 3
    # as the m/i/c is not actually used on the forum code (can't have / in slugs)
    #(r'^discuss/m/', include('forum.urls')),
    #(r'^discuss/i/', include('forum.urls')),
    #(r'^discuss/c/', include('forum.urls')),

    (r'^questions/', include('spenglr.questions.urls')),
    #(r'^resources/', include('spenglrcom.resources.urls')),


)

