from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Avg, Max, Min, Count

from package.models import UserPackage, Package

class Command(BaseCommand):
    args = ""
    help = "Update package total_questions and total_resources (post db import)"
    
    def handle(self, *args, **options):

        from wallextend.models import add_extended_wallitem

        packages = Package.objects.all()
        
        for package in packages:

            userpackages = package.userpackage_set.exclude(end_date=None).order_by('end_date')

            if userpackages:
                userpackage=userpackages[0]

                add_extended_wallitem(package.wall,userpackage.user,created_at=userpackage.end_date,template_name='package_1stcomplete.html',extra_context={
                                                        'package': package,
                                                        'userpackage': userpackage,
                                                        })            

            userpackages = package.userpackage_set.exclude(end_date=None).filter(percent_correct=100)
            if userpackages:
                for userpackage in userpackages:
                    add_extended_wallitem(package.wall,userpackage.user,created_at=userpackage.end_date,template_name='package_100pc.html',extra_context={
                                                            'package': package,
                                                            'userpackage': userpackage,
                                                            })       
                
                                                    
                                                            
