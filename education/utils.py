from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from spenglr.education.models import Module,Course,UserCourse,UserModule
# Python standard
import math
from datetime import date as _date



# Calculate mSQ for the oldest records
def batch_module_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = Module.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course


# Calculate cSQ for the oldest records
def batch_course_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = Course.objects.order_by('?')[:100]

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
def batch_usercourse_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = UserCourse.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course