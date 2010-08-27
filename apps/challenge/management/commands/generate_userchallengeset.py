from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import UserChallenge

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userchallenge in UserChallenge.objects.filter(challengeset=None):
            userchallenge.generate_challengeset()
            userchallenge.save()

