from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from concept.models import Concept

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for concept in Concept.objects.all():
            concept.total_questions = concept.questions.count()
            concept.total_resources = concept.resources.count()
            concept.save()
