from django.core.management import setup_environ
import settings
setup_environ(settings)
# Spenglr
from spenglr.questions.utils import batch_question_update_sq

def cron():
    batch_question_update_sq()
    


cron()