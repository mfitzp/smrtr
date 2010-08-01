from django import template
from django.template import resolve_variable, NodeList
from django.contrib.auth.models import User, Group
from django.utils.timesince import timesince


import datetime

register = template.Library()

@register.simple_tag
def duration( duration ):
    """ 
    Usage: {% duration seconds %} or {% duration timedelta %}
            Returns seconds duration as days, hours, minutes, seconds
            Based on core timesince/timeuntil
    """
    if duration:
        
        if isinstance( duration, datetime.timedelta ) != True:
            duration = datetime.timedelta(seconds = duration)
               
        base = datetime.datetime(1970,1,1) # Arbitrary date
        return timesince(base, base+duration)
        
    else:
        return ''


