from django.core.management import setup_environ
import settings
setup_environ(settings)
# Spenglr
from spenglr.questions.utils import *
from spenglr.education.utils import *

def cron():
    batch_question_update_sq()
    
    batch_course_update_sq()    
    batch_module_update_sq()

    batch_usercourse_update_sq()
    batch_usermodule_update_sq()

cron()