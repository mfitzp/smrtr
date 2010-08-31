from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from package.models import Package, PackageSet

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for packageset in PackageSet.objects.filter(package=0):
            packages = Package.objects.all()
            
            for challenge in packageset.challenges.all():
                packages = packages.filter(challenges=challenge)
                
            if packages:
                packageset.package = packages[0]
                packageset.save()
