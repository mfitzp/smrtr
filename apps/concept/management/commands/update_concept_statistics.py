from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from concept.models import UserConcept

class Command(BaseCommand):
    args = ""
    help = "Update concept total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userconcept in UserConcept.objects.all():
            userconcept.update_statistics()
            userconcept.update_focus()
            userconcept.save()
