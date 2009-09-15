from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login

class RequireLoginMiddleware(object):

    def __init__( self ):
        self.loginpath = getattr( settings, 'LOGIN_URL' )
    
    def process_request( self, request ):
        if request.user.is_anonymous() and request.path != self.loginpath:
            if request.POST:
                return login( request )
            else:
                return HttpResponseRedirect('%s?next=%s' % (self.loginpath, request.path))
