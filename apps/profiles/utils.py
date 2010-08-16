from django.conf import settings
from django.db.models import Avg, Max, Min, Count, StdDev, F
from django.contrib.auth.models import User

# Python standard
import math
from datetime import date as _date
# Smrtr
from profiles.models import UserProfile
# External
from notification import models as notification

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
    # Store previous SQ value
    UserProfile.objects.all().update( previous_sq=F('sq') )
    #UPDATE {spenglr_users} SET  nuSQ = 100 + ( ( ( uSQ - %d ) / %d ) * 16) WHERE questions_attempted>0
    UserProfile.objects.all().update( sq= 100 + ( ( ( F('calculated_sq') - d['avg_sq'] ) / d['stddev_sq'] ) * 16 ) )

    # Limit: this is horrible but using min() max() does not work on above query
    UserProfile.objects.filter(sq__gt=200).update( sq=200 )
    UserProfile.objects.filter(sq__lt=0).update( sq=0 )

    users_sq_changed = UserProfile.objects.exclude(sq=F('previous_sq'))
    for userp in users_sq_changed:
        notification.send([userp.user], "user_sq_updated", {"user": userp.user})        



def searchqueryset_profile_boost( request, sqs ):
    # Apply profile/local-boost
    profile = request.user.get_profile()

    if profile.country:
        sqs = sqs.boost( str('iso3'+profile.country.iso3).lower() , 20 )

    boost = list()
    # Cannot boost on phrase with spaces use (hopefully unique) iso3+code string to avoid text-clashes
    if profile.city:
        boost.extend( profile.city.split() ) #New York
    if profile.state:
        boost.extend( profile.state.split() ) #New Mexico

    for b in boost:
        sqs = sqs.boost( b.lower(), 2 ) # Need to boost with lowercase
        
    return sqs


