from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Spenglr
from questions.models import Question
# Python standard
import math
from datetime import date as _date


# qSQ CALCULATION
# Calculate qSQ for the oldest records
def batch_question_update_sq():

    # Retrieve 20 questions that have recently been answered and recalculates the SQ on these
    questions = Question.objects.filter(userquestionattempt__created__isnull=False).order_by('userquestionattempt__created')[:20]

    for q in questions:
        q.update_sq() # Call SQ recalculation for this question
        
        
def batch_question_update_ttc():
    
    # Retrieve 20 questions that have recently been answered and recalculates the ttc on these
    questions = Question.objects.filter(userquestionattempt__created__isnull=False).order_by('userquestionattempt__created')[:20]

    for q in questions:
        q.update_ttc() # Call SQ recalculation for this question

