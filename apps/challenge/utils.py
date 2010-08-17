from django.conf import settings
from django.db.models import Q
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
# Challenges are combinations of concepts (from the same topic, from user's perspective)
# Once a combination has been identified as most beneficial for the user, look for existing
# challenges the user has not attempted. Allows for multi-user competition, and cross-course competition
# Called on login to ensure always X challenges available, can be re-run on demand
# by the user once initial set of challenges have been completed.
def generate_userchallenges(user, number = None):

    # FIXME: This is all a bit horrible and hacky. It is difficult to do using Djangos query API directly
    # may be worth building SQL query to nab most of this in one go and save the looping

    # No value passed, auto-calc number to generate for user to reach CHALLENGES_MIN_ACTIVE
    if number == None:
        number = CHALLENGES_MIN_ACTIVE - user.userchallenge_set.filter(status__lt=2).count()

    if number > 0: # Save db hits if generating nothing at all
    
        # Iterate concepts, combine into topic-groups, maximum of 3 (configurable?), then stack up to post-process
        # leftovers are carried over if < 5 total challenges generated (configurable?)

        final = list()
        build = dict()
        
        # Full list of user's concepts, in descending focus (highest focus first)
        userconcepts = UserConcept.objects.filter(user=user).exclude(focus=0).exclude(concept__total_questions=0).order_by('-focus','?')
        # Iterate userconcepts 
        try:
            for userconcept in userconcepts:
                # Find topics the user is studying this concept on
                topics = userconcept.concept.topic_set.filter(usertopic__user=user)
                # Add this concept to the topic stacks
                for topic in topics:
                    # If started add to existing stack, otherwise create new
                    try:
                        build[topic.id].append(userconcept.concept.id)
                    except:
                        build[topic.id] = [ userconcept.concept.id ]
                        
                    # If we manage to build a list of 3, add to the final list
                    if len(build[topic.id]) == 3:
                        final.append([topic.id, build[topic.id]])
                        build[topic.id] = list()

                    if len(final) == number:
                        raise StopIteration() # We have enough in the final list, drop out of nested loop

            # Cleanup after the above for loop
            else:
                iterate = number - len(final)
                for b in build:
                    if iterate == 0:
                        break
                    iterate = iterate -1 
                    final.append([b, build[b]])

        except StopIteration:
            pass
            
        # Now we have a list of lists containing the topic id and the concept ids
        # [[16L, [68L, 70L, 78L]], [16L, [69L]], [305L, [99L]], [293L, [97L, 90L]]]
        # Iterate top list (topic keyed)
        
        #TODO: Look for already existing, open, challenges to allow for multi-player as default
        for mlist in final:
            # For clarity
            topic_id = mlist[0]
            concept_ids = mlist[1]
            # Look for existing challenges matching (exact) this set of concepts
            # Make sure the user has not previously attempted the challenge
            # Build search filter (exclude challenges user has already been assigned to)
            cs = Challenge.objects.exclude(userchallenge__user=user)
            for concept_id in concept_ids:
                cs = cs.filter(concepts__id=concept_id)
            
            # We have found (a) challenge
            if cs:            
                challenge=cs[0]
            else:
                challenge = Challenge()
                challenge.user = user
                challenge.save()
                    
                # Iterate concepts
                # mlist[1] is the list-within ie. [68,70,78] above
                for concept_id in concept_ids:
                    challenge.concepts.add(Concept.objects.get(pk=concept_id))            
            
                challenge.generate_name()
                # Now populate question lists based on current settings
                challenge.generate_questions()
                challenge.save()

            # We have the challenge created, now generate the userchallenge to link and assign
            # now shows up in the user's list. Magic.
            userchallenge = UserChallenge()
            userchallenge.challenge = challenge
            userchallenge.user = user
            userchallenge.save()

# Calculate SQ for the usercourse records with most recently updated usertopics
def batch_generate_userchallenges():

    # Random 100 users
    # NOTE: Fix to something more sensible
    objects = User.objects.order_by('?')[:100]

    for o in objects:
        generate_userchallenges(o)





def generate_userchallenges_on_adding_usertopic(sender, created, **kwargs):
    # Check saving this userchallenge for first time (do not trigger on SQ updates/etc)
    if created:
        usertopic = kwargs['instance']
        generate_userchallenges(usertopic.user, 2)

post_save.connect(generate_userchallenges_on_adding_usertopic, sender=UserTopic)


