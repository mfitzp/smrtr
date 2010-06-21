from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math
from datetime import date as _date
from django.contrib.auth.models import User
# Spenglr
from settings import CHALLENGES_MIN_ACTIVE
from education.models import *
from challenge.models import *

# Check if challenges exist for a given user and if not, generate
# Called on login to ensure always X challenges available, can be re-run on demand
# by the user once initial set of challenges have been completed.
def generate_user_challenges(user, number = CHALLENGES_MIN_ACTIVE):

    # FIXME: This is all a bit horrible and hacky. It is difficult to do using Djangos query API directly
    # may be worth building SQL query to nab most of this in one go and save the looping
    
    # Iterate concepts, combine into module-groups, maximum of 3 (configurable?), then stack up to post-process
    # leftovers are carried over if < 5 total challenges generated (configurable?)

    final = list()
    build = dict()
    
    # Full list of user's concepts, in descending focus (highest focus first)
    userconcepts = UserConcept.objects.filter(user=user).order_by('-focus')
    # Iterate userconcepts 
    for userconcept in userconcepts:
        # Find modules the user is studying this concept on
        modules = userconcept.concept.module_set.filter(usermodule__user=user)
        # Add this concept to the module stacks
        for module in modules:
            # If started add to existing stack, otherwise create new
            try:
                build[module.id].append(userconcept.concept.id)
            except:
                build[module.id] = [ userconcept.concept.id ]
                
            # If we manage to build a list of 3, add to the final list
            if len(build[module.id]) == 3:
                final.append([module.id, build[module.id]])
                build[module.id] = list()
    # Cleanup after the above for loop
    else:
        iterate = number - len(final)
        for b in build:
            if iterate == 0:
                break
            iterate = iterate -1 
            final.append([b, build[b]])

    # Now we have a list of lists containing the module id and the concept ids
    # [[16L, [68L, 70L, 78L]], [16L, [69L]], [305L, [99L]], [293L, [97L, 90L]]]
            
    # Iterate top list (module keyed)
    for mlist in final:
        challenge = Challenge()
        challenge.user = user
        challenge.save()
                
        # Iterate concepts
        # mlist[1] is the list-within ie. [68,70,78] above
        for concept_id in mlist[1]:
            challenge.concepts.add(Concept.objects.get(pk=concept_id))            
        
        challenge.generate_name()
        # Now populate question lists based on current settings
        challenge.update_questions()
        challenge.save()

        userchallenge = UserChallenge()
        userchallenge.challenge = challenge
        userchallenge.user = user
        userchallenge.save()

# Calculate SQ for the usercourse records with most recently updated usermodules
def batch_generate_user_challenges():

    # Random 100 courses
    # NOTE: Fix to something more sensible
    objects = User.objects.order_by('?')[:100]

    for o in objects:
        if o.userchallenge_set.filter(status__lt=2).count() == 0:
            generate_user_challenges(o) # Call SQ recalculation for this course
    

