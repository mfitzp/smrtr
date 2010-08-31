from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from challenge.models import Challenge,UserChallenge


# Calculate cSQ for the oldest records
def batch_challenge_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one question
    objects = Challenge.objects.filter(questions__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()


# Calculate SQ for the usercourse records with most recently updated userpackages
def batch_userchallenge_update_sq():

    # Random 100 courses
    # FIXME: Fix to something more sensible

    objects = UserChallenge.objects.exclude(percent_complete=0).exclude(percent_correct=None).filter(sq=None)[:100]
    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()

    objects = UserChallenge.objects.exclude(percent_complete=0).exclude(percent_correct=None).order_by('?')[:50]
    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()
                               
def batch_userchallenge_update_focus():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserChallenge.objects.order_by('?')[:100]

    for o in objects:
        o.update_focus() # Call focus recalculation for this course
        o.save()        
        
def batch_userchallenge_update_statistics():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserChallenge.objects.order_by('?')[:100]

    for o in objects:
        o.update_statistics() # Call focus recalculation for this course 
        o.save()        


