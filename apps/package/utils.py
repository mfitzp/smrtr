from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from package.models import Package,Challenge,UserPackage,UserChallenge


# Calculate mSQ for the oldest records
def batch_package_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one challenge
    objects = Package.objects.filter(challenges__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()

# Calculate SQ for the userpackage records with most recently answered questions
def batch_userpackage_update_sq():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    # Prioritise those with no SQ value
    objects = UserPackage.objects.exclude(percent_complete=0).exclude(percent_correct=None).filter(sq=None)[:100]
    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()

    objects = UserPackage.objects.exclude(percent_complete=0).exclude(percent_correct=None).order_by('?')[:50]
    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        o.save()


# Calculate SQ for the userpackage records with most recently answered questions
def batch_userpackage_update_statistics():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserPackage.objects.order_by('?')[:100]

    for o in objects:
        o.update_statistics() # Call SQ recalculation for this course               
        o.save()
