from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import UserChallenge
from education.models import Topic


class Command(BaseCommand):
    args = ""
    help = "Update challenge total_questions and total_resources (post db import)"
    
    def handle(self, *args, **options):
        for uc in UserChallenge.objects.filter(topic=None):
            uc.generate_topic()
            uc.save
            
             
