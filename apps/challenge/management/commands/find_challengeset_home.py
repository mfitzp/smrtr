from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import Challenge, ChallengeSet

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for challengeset in ChallengeSet.objects.filter(challenge=0):
            challenges = Challenge.objects.all()
            
            for concept in challengeset.concepts.all():
                challenges = challenges.filter(concepts=concept)
                
            if challenges:
                challengeset.challenge = challenges[0]
                challengeset.save()
