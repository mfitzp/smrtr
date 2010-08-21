from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import Challenge, UserChallenge
from resources.models import Resource
from django.conf import settings
from django.db.models import Avg, Max, Min, Count

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_questions and total_resources (post db import)"
    
    def handle(self, *args, **options):

        from wallextend.models import add_extended_wallitem

        challenges = Challenge.objects.filter(userchallenge__status=2).exclude(userchallenge__completed=None)
        
        for challenge in challenges:
            userchallenge = challenge.userchallenge_set.order_by('-completed')[0]
            
            add_extended_wallitem(challenge.wall,userchallenge.user,template_name='challenge_1stcomplete.html',extra_context={
                                                    'body':'is the first to complete!',
                                                    'challenge': challenge,
                                                    'userchallenge': userchallenge,
                                                    })            
