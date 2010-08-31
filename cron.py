from django.core.management import setup_environ
import settings
import datetime
setup_environ(settings)
from django.db.models import Avg, Max, Min, Count, Q
from django.contrib.sitemaps import ping_google
# Smrtr
from questions.utils import *
from challenge.utils import *
from package.utils import *
from profiles.utils import *
from network.utils import *

def cron():

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update question SQ..."
    batch_question_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update question ttc..."
    batch_question_update_ttc()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update challenge SQ..."
    batch_challenge_update_sq()    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update package SQ..."
    batch_package_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update network SQ..."
    batch_network_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user profile SQ..."
    batch_user_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Normalise user profile SQ..."
    batch_user_normalise_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user challenge SQ..."
    batch_userchallenge_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user package SQ..."
    batch_userpackage_update_sq()

    # Following are now calculated on completion of packages
    # print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user challenge statistics..."
    # batch_userchallenge_update_statistics()
    # print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user package statistics..."
    # batch_userpackage_update_statistics()
    
    # Still calculate this on cron as focus can change overtime
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user challenge focus..."
    batch_userchallenge_update_focus()

    # Don't ping google with sitemap when developing (be nice)
    from settings import DEBUG
    if DEBUG == False:
        print datetime.datetime.now().strftime(' %H:%M:%S') + ": Pinging Google with sitemap..."
        ping_google()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Done."
cron()
