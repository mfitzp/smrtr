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
    if prevsq is None or sq is None:
        difficulty = 'unknown'
    elif sq > prevsq:
        change = 'up'
    elif sq < prevsq:
        change = 'down'
    else:
        change = 'nochange'     

    return '<span class="sq %s">%d</span>' % (change, sq)


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

    # Limit SQ to the range 149-69
    sq = min( max( sq , 69  ) , 149 )
    # Convert to 14-6
    sq = int( math.floor( sq / 10) )

    descriptive = {
        14: "Genius",
        13: "Very Superior",
        12: "Superior",
        11: "High Average",
        10: "Average",
        9 : "Average",
        8 : "Low Average",
        7 : "Very Low",
        6 : "Extremely Low",
    }[sq]

    return descriptive