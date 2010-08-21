from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import Challenge
from resources.models import Resource

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_questions and total_resources (post db import)"
    
    def handle(self, *args, **options):
        for challenge in Challenge.objects.all():
            ucs=challenge.userchallenge_set.exclude(topic=None)
            if ucs:
                uc = ucs[0]
                challenge.name = uc.topic.name
                challenge.image = uc.topic.image
                challenge.save()
