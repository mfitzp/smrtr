from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext   
from django.core.exceptions import PermissionDenied    
from django.contrib.auth.views import login

from core.views import *

class RequireLoginMiddleware(object):

    def __init__( self ):
        # Root path for registration/accounts (/accounts)
        self.loginpath = getattr( settings, 'LOGIN_PATH' )
        # Login url (/accounts/login)
        self.loginurl  = getattr( settings, 'LOGIN_URL' )
    
    def process_request( self, request ):
        # Not logged in, and target path is not in login/registration path
        if request.user.is_anonymous():
            if ( request.path.startswith(self.loginpath) or request.path == '/' ) != True:
                if request.POST:
                    return login( request )
                else:
                    return HttpResponseRedirect('%s?next=%s' % (self.loginurl, request.path))
                        
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_anonymous() and view_func == home:
            return intro( request )
            
   
