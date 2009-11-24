from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from spenglr.questions.models import Question
# Python standard
import math
from datetime import date as _date


# qSQ CALCULATION
# Calculate qSQ for the oldest records
def batch_question_update_sq():

    # Retrieve 20 questions that have recently been answered and recalculates the SQ on these
    questions = Question.objects.filter(userquestionattempt__created__isnull=False).order_by('userquestionattempt__created')[:20]

    for q in questions:
        print q.id
        q.update_sq() # Call SQ recalculation for this question