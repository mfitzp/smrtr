from django.core.management import setup_environ
import settings
import datetime
setup_environ(settings)

from django.contrib.sitemaps import ping_google
# Smrtr
from questions.utils import *
from education.utils import *
from challenge.utils import *
from profiles.utils import *
from network.utils import *

def cron():

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update question SQ..."
    batch_question_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update question ttc..."
    batch_question_update_ttc()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update concept SQ..."
    batch_concept_update_sq()    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update module SQ..."
    batch_module_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update network SQ..."
    batch_network_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user profile SQ..."
    batch_user_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Normalise user profile SQ..."
    batch_user_normalise_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user concept SQ..."
    batch_userconcept_update_sq()
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user module SQ..."
    batch_usermodule_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user concept focus..."
    batch_userconcept_update_focus()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user concept percent complete..."
    batch_userconcept_update_percent_complete()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user module percent complete..."
    batch_usermodule_update_percent_complete()
    

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Generating challenges..."
    batch_generate_userchallenges()

    # Don't ping google with sitemap when developing (be nice)
    from settings import DEBUG
    if DEBUG == False:
        print datetime.datetime.now().strftime(' %H:%M:%S') + ": Pinging Google with sitemap..."
        ping_google()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Done."
cron()
