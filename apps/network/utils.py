from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
# Spenglr
from network.models import Network

# Calculate mSQ for the oldest records
def batch_network_update_sq():

    # Random 1000 networks
    # NOTE: Fix to something more sensible
    # + where at least one member
    
    objects = Network.objects.filter(usernetwork__isnull=False).order_by('?')[:100]

    for o in objects:
        o.update_sq() # Call SQ recalculation for this course