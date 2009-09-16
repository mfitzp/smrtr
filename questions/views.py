from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from spenglr.questions.models import Question
from spenglr.education.models import Module
#from spenglr.study.models import UserQuestions


def questions(request, module_id):
    
    module = Module.objects.get(pk=module_id)
    questions = module.question_set.order_by('?')

    return render_to_response('questions/question_list.html', {'module': module, 'questions': questions})

