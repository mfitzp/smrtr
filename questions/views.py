from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.questions.models import Question, Answer
from spenglr.education.models import Module
#from spenglr.study.models import UserQuestions


def questions(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    questions = module.question_set.order_by('?')

    return render_to_response('questions/question_list.html', {'module': module, 'questions': questions})


def submit(request, module_id):

    total_correct = 0
    total_incorrect = 0
    total_answered = 0
    questions = list()

    module = get_object_or_404(Module, pk=module_id)

    for key in request.POST.keys():

        try:
            # Check that this is a question-response variable
            # Using split will throw exception if not present
            qid = key.split('questions-')[1]
            # Load question object
            q = Question.objects.get(pk=qid)
            
            # Find submitted answer id in the list of correct answers
            aid = request.POST.get('questions-' + qid)
            total_answered = total_answered + 1

            try:
                correct = q.answer_set.get(pk=aid, is_correct=True)
            except:
                total_incorrect = total_incorrect + 1
            else:
                total_correct = total_correct + 1

            # Add this question to the question list for review on the summary page
            q.answered = int(aid)
            questions.append(q)

            # Remove this question from the user's question queue
            

        except:
            pass

    return render_to_response('questions/question_list_answered.html', {'module': module, 'questions': questions })
