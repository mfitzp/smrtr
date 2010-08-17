from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from education.models import Topic,Concept,UserTopic,UserConcept


# Calculate mSQ for the oldest records
def batch_topic_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    # + where at least one concept
    objects = Topic.objects.filter(concepts__isnull=False).order_by('?')[:100]

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



# Calculate SQ for the usertopic records with most recently answered questions
def batch_usertopic_update_sq():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserTopic.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course

# Calculate SQ for the usercourse records with most recently updated usertopics
def batch_userconcept_update_sq():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserConcept.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
        
                               
def batch_userconcept_update_focus():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserConcept.objects.order_by('?')[:100]

    for o in objects:
        o.update_focus() # Call focus recalculation for this course
        
        
def batch_userconcept_update_percent_complete():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserConcept.objects.order_by('?')[:100]

    for o in objects:
        o.update_percent_complete() # Call focus recalculation for this course 
        
# Calculate SQ for the usertopic records with most recently answered questions
def batch_usertopic_update_percent_complete():

    # Random 100 courses
    # FIXME: Fix to something more sensible
    objects = UserTopic.objects.order_by('?')[:100]

    for o in objects:
        o.update_percent_complete() # Call SQ recalculation for this course               

