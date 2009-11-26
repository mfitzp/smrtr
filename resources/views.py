from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
# Spenglr
from questions.models import Question
from education.models import Module



def questions(request, module_id):
    
    module = Module.objects.get(pk=module_id)
    questions = module.question_set.order_by('?')

    return render_to_response('questions/question_list.html', {'module': module, 'questions': questions})

