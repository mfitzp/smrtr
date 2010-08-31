from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from challenge.models import Challenge

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for challenge in Challenge.objects.all():
            challenge.total_questions = challenge.questions.count()
            challenge.total_resources = challenge.resources.count()
            challenge.save()
