from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from spenglr.education.models import Module,Course
# Python standard
import math
from datetime import date as _date


# mSQ CALCULATION
# Calculate mSQ for the oldest records
def batch_module_update_sq():

    # Random 100 modules
    # NOTE: Fix to something more sensible
    modules = Module.objects.order_by('?')[:100]

    for m in modules:
        m.update_sq() # Call SQ recalculation for this module

# cSQ CALCULATION
# Calculate cSQ for the oldest records
def batch_course_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    courses = Course.objects.order_by('?')[:100]

    for c in courses:
        c.update_sq() # Call SQ recalculation for this course