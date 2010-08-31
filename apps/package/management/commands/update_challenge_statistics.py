from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from package.models import UserPackage

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userpackage in UserPackage.objects.all():
            userpackage.update_statistics()
            userpackage.save()
