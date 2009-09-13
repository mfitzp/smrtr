from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'spenglr.core.views.index'),
    (r'^login/$', 'spenglr.core.views.loginhandler'),

    (r'^education/', include('spenglr.education.urls')),
    (r'^study/', include('spenglr.study.urls')),

)
