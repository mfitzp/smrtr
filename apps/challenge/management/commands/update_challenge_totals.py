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
            challenge.total_questions = challenge.questions.count()
            challenge.total_resources = Resource.objects.filter(concepts__challenge=challenge).count()
            challenge.save()
