from django.core.management import setup_environ
import settings
import datetime
setup_environ(settings)
# Spenglr
from questions.utils import *
from education.utils import *
from challenge.utils import *
from profiles.utils import *
from network.utils import *

def cron():
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update question SQ/ttc..."
    batch_question_update_sq()
    batch_question_update_ttc()
    
    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update network, module & concept SQ..."
    batch_module_update_sq()
    batch_concept_update_sq()    
    batch_network_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user profile SQ..."
    batch_user_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user module & concept SQ..."
    batch_usermodule_update_sq()
    batch_userconcept_update_sq()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Update user cocept focus..."
    batch_userconcept_update_focus()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Generating challenges..."
    batch_generate_user_challenges()

    print datetime.datetime.now().strftime(' %H:%M:%S') + ": Done."
cron()
