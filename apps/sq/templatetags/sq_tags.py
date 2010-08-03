from django import template
from django.conf import settings
from django.template import resolve_variable, NodeList
# Python standard
import math

register = template.Library()

@register.simple_tag
def sqchange( prevsq, sq ):
    """ 
    Usage: {% sqchange sq prevsq %}
            Returns up down nochange
    """   
    if prevsq is None:
        prevsq = 100
    
    if sq is None:
        return '<span class="sq nochange">tbc</span>'

    if sq > prevsq:
        change = 'up'
    elif sq < prevsq:
        change = 'down'
    else:
        change = 'nochange'   
        
    from sq.utils import sq_division
    level = sq_division(sq)

    return '<span class="sq %s sq%s">%d</span>' % (change, level, sq)


@register.simple_tag
def sqdifficulty( usersq, diffsq ):
    """ 
    Usage: {% sqdifficulty usersq diffsq %}
            Returns difficulty of diffsq relative to usersq
    """   

    if usersq is None or diffsq is None:
        difficulty = 'unknown'
    elif usersq > diffsq + ( settings.SQ_FAIR_RANGE * 2 ):
        difficulty = 'easy'
    elif usersq > diffsq + settings.SQ_FAIR_RANGE:
        difficulty = 'simple'
    elif usersq > diffsq - settings.SQ_FAIR_RANGE:
        difficulty = 'fair'     
    elif usersq > diffsq - ( settings.SQ_FAIR_RANGE * 2):
        difficulty = 'tricky'     
    else:
        difficulty = 'hard'

    return '<span class="sq %s">%s</span>' % (difficulty, difficulty.capitalize())

@register.simple_tag
def sqdescriptive( sq ):
    """ 
    Usage: {% sqdescriptive sq %}
            Returns description of SQ level (IQ comparison)
            Very superior   2.2%
            120-129 Superior    6.7%
            110-119 High average    16.1%
            90-109  Average 50%
            80-89   Low average 16.1%
            70-79   Borderline  6.7%
            Below 70    Extremely low
    """  

    if sq is None:
        return "Unknown"

    # sq_division limits to range 14-6 based on sq input
    from sq.utils import sq_division
    
    descriptive = {
        9 : "Genius",
        8 : "Very Superior",
        7 : "Superior",
        6 : "High Average",
        5 : "Average",
        4 : "Average",
        3 : "Low Average",
        2 : "Very Low",
        1 : "Extremely Low",
    }[sq_division(sq)]

    return '%s' % (descriptive)
    
    

