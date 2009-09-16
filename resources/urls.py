from django.conf.urls.defaults import *
from spenglr.education.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

        #(r'^m/(?P<module_id>\d+)$', 'spenglr.questions.views.questions' ),

)
