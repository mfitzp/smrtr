from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from education.models import Concept

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for concept in Concept.objects.all():
            concept.total_questions = concept.question_set.count()
            concept.save()
