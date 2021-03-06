from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
# Spenglr
from questions.models import Question, Answer, UserQuestionAttempt
from package.models import Package
from resources.models import Resource, UserResource
# External
from tagging.models import Tag,TaggedItem

def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render_to_response('question_detail.html', {'question': question}, context_instance=RequestContext(request))

def latest_questions_package(request, package_id):
    
    package = get_object_or_404(Package, pk=package_id)

    questions = package.question_set.order_by('updated')

    return render_to_response('package_question_archive.html', {'package': package, 'questions': questions})

def questions_tagged(request,tag_id):
    tag = Tag.objects.get(pk=tag_id)
    questions = TaggedItem.objects.get_by_model(Question, tag)

    return render_to_response('question_tag_list.html', {'tag': tag, 'questions': questions}, context_instance=RequestContext(request))
