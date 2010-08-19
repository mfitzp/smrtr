# Python
import math
import urllib
# Django
from django import template
from django.conf import settings
from django.template import resolve_variable, NodeList
from django.utils.hashcompat import md5_constructor
from django.utils.html import escape
# External
from easy_thumbnails.files import get_thumbnailer



register = template.Library()

@register.simple_tag
def avatar( user, size=50 ):
    """ 
    Usage: {% avatar user [size] [force] %}
            Returns image tag for avatar image at given size
            Force enforces the source of the image
    """   
    
    if user.get_profile().avatar:
        # Use user-defined onsite avatar by default
        url = profile_avatar_url( user, size )
    
    elif hasattr(user, 'facebook_profile'):
        # If user has come in via facebook use their facebook image     
        url = facebook_avatar_url( user ) # Size is not used by facebook standard square, resized by html
        
    else:
        # Use gravatar as backup (with backup to local default url if no gravatar user)
        url = gravatar_url( user, size )


    return '<img src="%s" style="width:%dpx;height:%dpx">' % (url, size, size)

@register.simple_tag
def avatar_from_provider( user, size=50, provider='profile'):

    if provider=='profile':
        url = profile_avatar_url( user, size )

    elif provider=='facebook':
        # If user has come in via facebook use their facebook image     
        url = facebook_avatar_url( user )
        
    elif provider=='gravatar':
        # Use gravatar as backup (with backup to local default url if no gravatar user)
        url = gravatar_url( user, size )

    return '<img src="%s" style="width:%dpx;height:%dpx">' % (url, size, size)




def profile_avatar_url( user, size=50 ):

    # Thumbnail uploaded image to correct size
    thumbnail = get_thumbnailer(user.get_profile().avatar).get_thumbnail( dict(size=(size, size), crop=True ) )
    return escape( thumbnail.url )


def facebook_avatar_url( user ):

    fb = user.facebook_profile
    return escape( "http://graph.facebook.com/%s/picture?type=square" % (fb.username) )

def gravatar_url( user, size=50 ):

    gravatar_options = {
        's': str(size), 
        'r': 'g'
        }
    gravatar_options['d'] = getattr(settings, 'AVATAR_DEFAULT_URL', '')
    return "http://www.gravatar.com/avatar/%s?%s" % (
        md5_constructor(user.email).hexdigest(),
        urllib.urlencode(gravatar_options),)


