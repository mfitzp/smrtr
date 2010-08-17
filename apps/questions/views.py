from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
# Spenglr
from questions.models import Question, Answer, UserQuestionAttempt
from education.models import Concept
from resources.models import Resource, UserResource
# External
from tagging.models import Tag,TaggedItem

def question_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render_to_response('question_detail.html', {'question': question}, context_instance=RequestContext(request))

def latest_questions_topic(request, topic_id):
    
    topic = get_object_or_404(Topic, pk=topic_id)

    questions = topic.question_set.order_by('last_updated')

    return render_to_response('topic_question_archive.html', {'topic': topic, 'questions': questions})

def questions_tagged(request,tag_id):
    tag = Tag.objects.get(pk=tag_id)
    questions = TaggedItem.objects.get_by_model(Question, tag)

    return render_to_response('question_tag_list.html', {'tag': tag, 'questions': questions}, context_instance=RequestContext(request))
