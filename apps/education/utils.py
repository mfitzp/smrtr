from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from education.models import Module,Concept,UserModule,UserConcept


# Calculate mSQ for the oldest records
def batch_module_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one concept
    objects = Module.objects.filter(concepts__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course

# Calculate cSQ for the oldest records
def batch_concept_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one question
    objects = Concept.objects.filter(question__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course



# Calculate SQ for the usermodule records with most recently answered questions
def batch_usermodule_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = UserModule.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course

# Calculate SQ for the usercourse records with most recently updated usermodules
def batch_userconcept_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = UserConcept.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
