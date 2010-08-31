from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum
# Smrtr
from package.models import PackageSet,UserPackageSet,UserPackage
from questions.models import UserQuestionAttempt

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for userpackage in UserPackage.objects.exclude(end_date=None):
            o = UserPackageSet.objects.filter(user=userpackage.user, packageset__package=userpackage.package).exclude(completed=None).aggregate(Max('completed'))
            if o:
                if o['completed__max'] is not None:
                    userpackage.end_date = o['completed__max']
                    userpackage.save()
                else:
                    # Get from latest question
                    o = UserQuestionAttempt.objects.filter(user=userpackage.user, question__challenges__package=userpackage.package).aggregate(Max('created'))
                    userpackage.end_date = o['created__max']
                    userpackage.save()
