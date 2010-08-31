from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from package.models import PackageSet
from resources.models import Resource
from questions.models import Question

class Command(BaseCommand):
    args = ""
    help = "Update challenge total_question counts (post db import)"
    
    def handle(self, *args, **options):
        for packageset in PackageSet.objects.all():
            packageset.total_questions = packageset.questions.count()
            packageset.total_resources = Resource.objects.filter(challenges__packageset=packageset).count()
            packageset.save()
