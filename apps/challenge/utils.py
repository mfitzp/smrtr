from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from challenge.models import Challenge,Concept,UserChallenge,UserConcept


# Calculate mSQ for the oldest records
def batch_challenge_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one concept
    objects = Challenge.objects.filter(concepts__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()

# Calculate SQ for the userchallenge records with most recently answered questions
def batch_userchallenge_update_sq():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserChallenge.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()

# Calculate SQ for the userchallenge records with most recently answered questions
def batch_userchallenge_update_statistics():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserChallenge.objects.order_by('?')[:100]

    for o in objects:
        o.update_statistics() # Call SQ recalculation for this course               
        o.save()
