from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import Challenge
from resources.models import Resource

class Command(BaseCommand):
    args = "<filename>"
    help = "Import questions, answers and tags from CSV"
    
    def handle(self, *args, **options):
        """Imports questions from CSV."""
        # Cause the default site to load.
        for challenge in Challenge.objects.all():
            challenge.total_questions = challenge.questions.count()
            challenge.total_resources = Resource.objects.filter(concepts__challenge=challenge).count()
            challenge.save()
