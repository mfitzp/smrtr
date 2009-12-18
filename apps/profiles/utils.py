from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from django.contrib.auth.models import User
# Python standard
import math
from datetime import date as _date
# Spenglr
from profiles.models import UserProfile

# Calculate mSQ for the oldest records
def batch_user_update_sq():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = UserProfile.objects.order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course
