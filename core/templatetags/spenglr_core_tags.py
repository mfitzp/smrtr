from django import template
from django.template import resolve_variable, NodeList
from django.contrib.auth.models import User, Group

register = template.Library()

@register.simple_tag
def whichgroups( user, grouplist ):
    """ 
    Usage: {% whichgroup user Admins|Group1|Group2 %}

    """
    for group in grouplist.split("|"):
        try:
            if Group.objects.get(name=group) in user.groups.all():
                return group
        except:
            continue
