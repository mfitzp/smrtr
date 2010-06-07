from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login

class RequireLoginMiddleware(object):

    def __init__( self ):
        # Root path for registration/accounts (/accounts)
        self.loginpath = getattr( settings, 'LOGIN_PATH' )
        # Login url (/accounts/login)
        self.loginurl  = getattr( settings, 'LOGIN_URL' )
    
    def process_request( self, request ):
        # No logged in, and target path is not in login/registration path
        if request.user.is_anonymous() and request.path.startswith(self.loginpath) != True:
            if request.POST:
                return login( request )
            else:
                return HttpResponseRedirect('%s?next=%s' % (self.loginurl, request.path))
