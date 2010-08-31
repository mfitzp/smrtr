from django.conf.urls.defaults import *
# Smrtr
from package.models import *
from package.forms import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    # Package generic
    url(r'^(?P<package_id>\d+)/$', 'package.views.detail',  name='package-detail'  ),
    url(r'^(?P<package_id>\d+)/providers/$', 'package.views.providers',  name='package-providers'  ),
    url(r'^(?P<package_id>\d+)/register/$', 'package.views.register',  name='package-register'  ),
    url(r'^(?P<package_id>\d+)/unregister/$', 'package.views.unregister',  name='package-unregister'  ),

    # Package creation and editing
    url(r'^create/$', 'package.views.create',  name='package-create'  ),
    url(r'^(?P<package_id>\d+)/edit/$', 'package.views.edit',  name='package-edit'  ),


    # Package search
    url(r'^search/$', 'package.views.search',  name='package-search'  ),


    # Package deprec
    url(r'^(?P<package_id>\d+)/newset/$', 'package.views.newset', name='package-newset'),
    url(r'^(?P<package_id>\d+)/newset/ajax/$', 'package.views.newset_ajax', name='package-newset-ajax'),
    url(r'^(?P<package_id>\d+)/challenges/add/', 'package.views.add_challenges', name='package-add-challenges' ),

)
