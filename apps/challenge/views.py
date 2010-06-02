from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
# Spenglr
from education.models import *
from network.models import *
from questions.models import *
from challenge.models import *
from challenge.forms import *
# External
from wall.forms import WallItemForm
from haystack.query import SearchQuerySet



# Create a new challenge
# Challenges are lists of questions to be attempted: they can be 
# built from concepts, modules, tags, etc. (passed in as parameters)
# Challenges may be public or private, and solo or group
# Scoring can be individual or network based (e.g. university vs. university, course vs. course)
def edit(request, challenge_id = None):

    if challenge_id:
        # id passed we are editing previous Challenge object
        challenge = get_object_or_404(Challenge, pk=challenge_id)
    else:
        # If no id passed, we create a new challenge object
        challenge = Challenge()
                
    if request.POST.get('name'):
    
        form = ChallengeForm(request.POST, instance=challenge)       
        
        if form.is_valid(): # All validation rules pass
            
            # Update challenge instance object and save
            challenge.name = form.cleaned_data['name']
            challenge.description = form.cleaned_data['description']
            challenge.user = request.user
            #challenge.concepts = form.cleaned_data['concepts']
            challenge.save()
            # Now populate question lists based on current settings
            challenge.update_questions()
            
            # Create userchallenge for the creating user (will need one anyway) and save
            userchallenge = UserChallenge()
            userchallenge.user = request.user
            userchallenge.challenge = challenge
            userchallenge.update_sq()
            userchallenge.save()
            
            return HttpResponseRedirect( reverse('challenge-do',kwargs={'challenge_id':challenge.id} ) ) # Redirect to challenge_do for this challenge
    
    else:
        prefill = {
            'name':request.GET.get('name'),
            'description':request.GET.get('description'),
            'total_questions':request.GET.get('total_questions'),
            'minsq':request.GET.get('minsq'),
            'maxsq':request.GET.get('maxsq'),
            }
        # TODO: Prefill concepts from csv list on query url
        # TODO: Prefill name/description (if not set yet) based on contents of concept list
        form = ChallengeForm(initial=prefill, instance=challenge) 

    context = { 
        'form': form,
        'challenge':challenge,
    }
    
    return render_to_response('challenge_edit.html', context, context_instance=RequestContext(request))    
  

def detail(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    #TODO: Access grant/deny
        
    # If the user has a challenge record retrieve it, or create a new one
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = list()            

    return render_to_response('challenge_view.html', {'challenge': challenge, 'userchallenge':userchallenge}, context_instance=RequestContext(request))




def do(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    #TODO: Access grant/deny
        
    # If the user has a challenge record retrieve it, or create a new one
    try:
        #TODO: Should only return if the challenge object is 'open'
        #UserChallenges should be closed on completion,re-attempts (if allowed)
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = UserChallenge()
        userchallenge.user = request.user
        userchallenge.challenge = challenge
        userchallenge.update_sq() # Initial value from previous answers to included questions
        userchallenge.save()              

    #TODO: How do we select questions from the challenge queue to present? 
    #If returning in order will need to keep progress flag in userchallenge object
    #makes more sense, and allows for 'completion' of challenge
    #FIXME: Return 10Qs in order, using progress flag in users bit
    questions = challenge.questions.order_by('?')[:10] # Returns 10 random questions

    return render_to_response('challenge_do.html', {'challenge': challenge, 'userchallenge':userchallenge, 'questions': questions}, context_instance=RequestContext(request))

def do_submit(request, challenge_id):

    totals = { 'correct': 0, 'incorrect': 0, 'answered': 0, 'percent': 1 }
    questions = list()

    challenge = get_object_or_404(Challenge, pk=concept_id)

    # If the user is registered on this concept pull record
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        # Not found
        #FIXME: Should this be another error code?
        raise Http404

    # Iterate over all POST keys and pull out the question answer question-n fields
    for key in request.POST.keys():

        try:
            # Check that this is a question-response variable
            # Using split will throw exception if not present
            qid = key.split('questions-')[1]
            # Load question object
            q = Question.objects.get(pk=qid)
            
        except:
            # Ignore errors and proceed to next POST key
            pass

        else:
            # We have a valid set of answer data, save to db
            totals['answered'] = totals['answered'] + 1

            # Preparer UserQuestionAttempt to save success/failure to db
            uqa = UserQuestionAttempt()
            uqa.question = q
            uqa.user = request.user
            uqa.usq = 100 #request.user.sq

            # Find submitted answer id in the list of correct answers
            aid = request.POST.get('questions-' + qid)
            try:
                correct = q.answer_set.get(pk=aid, is_correct=True)
            except:
                totals['incorrect'] = totals['incorrect'] + 1
                uqa.percent_correct = 0
            else:
                totals['correct'] = totals['correct'] + 1
                uqa.percent_correct = 100

            # Add this question to the question list for review on the summary page
            q.answered = int(aid)
            questions.append(q)

            # Save success/failure to the db
            uqa.save()

            # Remove this question from the user's question queue (NOTE: If implemented?)
            # TODO: Should throw an error on missing answers and enforce them
            # then advance challenge progress counter on completion ONLY

    totals['percent'] = ( 100 * totals['correct'] ) / totals['answered']

    # Recalculate SQ values for this module/usermodule_set  
    # NOTE: May need to remove this is load too great?
    userchallenge.update_sq()

    return render_to_response('challenge_do_submit.html', {'challenge': challenge,'userchallenge':userchallenge, 'questions': questions, 'totals': totals }, context_instance=RequestContext(request))


