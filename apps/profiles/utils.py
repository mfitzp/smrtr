from django.conf import settings
from django.db.models import Avg, Max, Min, Count, StdDev, F
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
        o.update_sq() # Call SQ recalculation for this user

def batch_user_normalise_sq():


    d = UserProfile.objects.aggregate(avg_sq=Avg('calculated_sq'),stddev_sq=StdDev('calculated_sq'))
    d['stddev_sq'] = max( 1, d['stddev_sq'] ) # Prevent <1 sd mean

    assert False, d
    # Store previous SQ value
    UserProfile.objects.all().update( previous_sq=F('sq') )
    #UPDATE {spenglr_users} SET  nuSQ = 100 + ( ( ( uSQ - %d ) / %d ) * 16) WHERE questions_attempted>0
    UserProfile.objects.all().update( sq= 100 + ( ( ( F('calculated_sq') - d['avg_sq'] ) / d['stddev_sq'] ) * 16 ) )

    #users_sq_changed = UserProfile.objects.filter( previous_sq__ne=F('sq') )
    #for user in changed:
    #    notification.send([user], "user_sq_updated", {"user": user})        
    #    self.save()
