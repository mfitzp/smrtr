from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Avg, Max, Min, Count

from challenge.models import UserChallenge, Challenge

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_questions and total_resources (post db import)"
    
    def handle(self, *args, **options):

        from wallextend.models import add_extended_wallitem

        challenges = Challenge.objects.all()
        
        for challenge in challenges:

            userchallenges = challenge.userchallenge_set.exclude(end_date=None).order_by('end_date')

            if userchallenges:
                userchallenge=userchallenges[0]

                add_extended_wallitem(challenge.wall,userchallenge.user,created_at=userchallenge.end_date,template_name='challenge_1stcomplete.html',extra_context={
                                                        'challenge': challenge,
                                                        'userchallenge': userchallenge,
                                                        })            

            userchallenges = challenge.userchallenge_set.exclude(end_date=None).filter(percent_correct=100)
            if userchallenges:
                for userchallenge in userchallenges:
                    add_extended_wallitem(challenge.wall,userchallenge.user,created_at=userchallenge.end_date,template_name='challenge_100pc.html',extra_context={
                                                            'challenge': challenge,
                                                            'userchallenge': userchallenge,
                                                            })       
                
                                                    
                                                            
