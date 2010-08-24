from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import ChallengeSet
from resources.models import Resource
from questions.models import Question

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for challengeset in ChallengeSet.objects.all():
            challengeset.total_questions = challengeset.questions.count()
            challengeset.total_resources = Resource.objects.filter(concepts__challengeset=challengeset).count()
            challengeset.save()
