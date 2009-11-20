from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.questions.models import Question, Answer
from spenglr.education.models import Module, ModuleInstance
#from spenglr.study.models import UserQuestions
from tagging.models import Tag,TaggedItem

def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render_to_response('questions/question_detail.html', {'question': question})


def questions(request, modulei_id):

    modulei = get_object_or_404(ModuleInstance, pk=modulei_id)
    module = modulei.module # Prefetch

    # If the user is registered on this module pull record
    try:
        usermodule = modulei.usermodule_set.get( user=request.user )
    except:
        usermodule = list()

    questions = module.question_set.order_by('?')[:10] # Returns 10 random questions

    return render_to_response('questions/question_list.html', {'module': module, 'modulei':modulei, 'usermodule':usermodule, 'questions': questions})

def submit(request, modulei_id):

    totals = { 'correct': 0, 'incorrect': 0, 'answered': 0, 'percent': 1 }
    questions = list()

    modulei = get_object_or_404(ModuleInstance, pk=modulei_id)
    module = modulei.module # Prefetch

    # If the user is registered on this module pull record
    try:
        usermodule = modulei.usermodule_set.get( user=request.user )
    except:
        usermodule = list()

    # Iterate over all POST keys and pull out the question answer question-n fields
    for key in request.POST.keys():

        try:
            # Check that this is a question-response variable
            # Using split will throw exception if not present
            qid = key.split('questions-')[1]
            # Load question object
            q = Question.objects.get(pk=qid)
            
            # Find submitted answer id in the list of correct answers
            aid = request.POST.get('questions-' + qid)
            totals['answered'] = totals['answered'] + 1

            try:
                correct = q.answer_set.get(pk=aid, is_correct=True)
            except:
                totals['incorrect'] = totals['incorrect'] + 1
            else:
                totals['correct'] = totals['correct'] + 1

            # Add this question to the question list for review on the summary page
            q.answered = int(aid)
            questions.append(q)

            # Remove this question from the user's question queue
            

        except:
            pass

    totals['percent'] = ( 100 * totals['correct'] ) / totals['answered']

    return render_to_response('questions/question_list_answered.html', {'module': module, 'modulei': modulei, 'usermodule':usermodule, 'questions': questions, 'totals': totals })


def latest_questions_module(request, module_id):
    
    module = get_object_or_404(Module, pk=module_id)

    questions = module.question_set.order_by('last_updated')

    return render_to_response('questions/module_question_archive.html', {'module': module, 'questions': questions})

def questions_tagged(request,tag_id):
    tag = Tag.objects.get(pk=tag_id)
    questions = TaggedItem.objects.get_by_model(Question, tag)

    return render_to_response('questions/question_tag_list.html', {'tag': tag, 'questions': questions})
