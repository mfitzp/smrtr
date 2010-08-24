from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import ChallengeSet,UserChallengeSet,UserChallenge
from django.db.models import Avg, Max, Min, Count, Sum

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userchallenge in UserChallenge.objects.exclude(end_date=None):
            o = UserChallengeSet.objects.filter(user=userchallenge.user, challengeset__challenge=userchallenge.challenge).exclude(completed=None).aggregate(Max('completed'))
            
            if o:
                if o['completed__max'] is not None:
                    userchallenge.end_date = o['completed__max']
                    userchallenge.save()
