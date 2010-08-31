from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import UserChallenge

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userchallenge in UserChallenge.objects.all():
            userchallenge.update_statistics()
            userchallenge.update_focus()
            userchallenge.save()
