from django import template
from django.template import resolve_variable, NodeList
from django.contrib.auth.models import User, Group

register = template.Library()

@register.simple_tag
def whichgroup( user ):
    """ 
    Usage: {% whichgroup user %}
            Returns a single group the user is a member of - used for 
            staff 'roles' (onsite cosmetic)
    """

    # Get a single record from this user's group listing, output the name
    if user.groups.get():
        return user.groups.get()
