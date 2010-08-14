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


@register.simple_tag
def classname( o ):
    """ 
    Usage: {% classname o %} 
            Returns classname of the object (for generic templates)
    """
    if duration:
        
        if isinstance( duration, datetime.timedelta ) != True:
            duration = datetime.timedelta(seconds = duration)
               
        base = datetime.datetime(1970,1,1) # Arbitrary date
        return timesince(base, base+duration)
        
    else:
        return ''

@register.filter
def classname(obj, arg=None):
    classname = obj.__class__.__name__.lower()
    if arg:
        if arg.lower() == classname:
            return True
        else:
            return False
    else:
        return classname

@register.simple_tag
def percentbar( num, addclass=None ):
    """ 
    Usage: {% percentbar num %} 
            Returns div bar for num percent
            Addclass is extra class definitions
    """
    if addclass:
        c = addclass
    else:
        c = ''
    
    if num > 0:
        num = max( 0, min( 100, num ) ) # Limit to 0-100
        #        return '<span class="sq %s sq%s">%d</span>' % (change, level, sq)
        return '<div class="percent-bar %s" style="width:%d%%"></div>' % (c, num)
    else:
        return ''
