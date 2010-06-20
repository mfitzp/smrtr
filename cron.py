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
    print datetime.now().strftime('%H:%M:%S') + ": Update SQ values..."
    batch_question_update_sq()
    
    batch_module_update_sq()
    batch_concept_update_sq()    

    print datetime.now().strftime('%H:%M:%S') + ": Update user SQ values..."

    batch_usermodule_update_sq()
    batch_userconcept_update_sq()
    batch_userconcept_update_focus()

    batch_user_update_sq()
    batch_network_update_sq()

    print datetime.now().strftime('%H:%M:%S') + ": Generating challenges..."
    batch_generate_user_challenges()

    print datetime.now().strftime('%A %d/%m/%Y %H:%M') + ": Done."
cron()
