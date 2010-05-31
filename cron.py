from django.core.management import setup_environ
import settings
setup_environ(settings)
# Spenglr
from questions.utils import *
from education.utils import *
from profiles.utils import *
from network.utils import *

def cron():
    batch_question_update_sq()
    
    batch_module_update_sq()
    batch_concept_update_sq()    

    batch_usermodule_update_sq()
    batch_userconcept_update_sq()

    batch_user_update_sq()
    batch_network_update_sq()

cron()