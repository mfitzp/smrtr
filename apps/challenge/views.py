from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.contrib.auth.decorators import login_required
import datetime
# Spenglr
from education.models import *
from network.models import *
from questions.models import *
from challenge.models import *
from challenge.forms import *
# External
from haystack.query import SearchQuerySet



# Create a new challenge
# Challenges are lists of questions to be attempted: they can be 
# built from concepts, modules, tags, etc. (passed in as parameters)
# Challenges may be public or private, and solo or group
# Scoring can be individual or network based (e.g. university vs. university, course vs. course)
@login_required
def create(request):
                
    if request.POST:
    
        form = ChallengeForm(request, request.POST)       
        form.fields['concepts'].queryset = Concept.objects.filter(userconcept__user=request.user)
                
        if form.is_valid(): # All validation rules pass
            
            # Update challenge instance object and save
            challenge = form.save(commit=False)
            challenge.user = request.user
            challenge.save()
            form.save_m2m()
            
            # Now populate question lists based on current settings
            challenge.update_questions()
            
            # Create userchallenge for the creating user (will need one anyway) and save
            UserChallenge(user=request.user, challenge=challenge).save()
            
            return redirect( 'challenge-do', {'challenge_id':challenge.id} ) # Redirect to challenge_do for this challenge
    
    else:
        form = ChallengeForm(request, request.GET) 
        # Provide concept-possibilities (from user's own lists)
        

    context = { 
        'form': form,
    }
    
    return render_to_response("challenge_edit.html", context, context_instance=RequestContext(request))    
 

def detail(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    #TODO: Access grant/deny
    
    # If the user has a challenge record retrieve it, or create a new one
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = None          

    context = {
        'challenge': challenge,
        'userchallenge':userchallenge,
        
        # List of previous/other challengers on this challenge
        'challengers_done':challenge.userchallenge_set.filter(status=2).order_by('-sq')[0:10],
        'challengers_todo':challenge.userchallenge_set.exclude(status=2).order_by('-sq')[0:10],
        }

    return render_to_response('challenge_view.html', context, context_instance=RequestContext(request))



@login_required
def do(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    #TODO: Access grant/deny
        
    # If the user has a challenge record retrieve it, or create a new one
    try:
        #TODO: If user has not 'completed' the challenge, allow through, otherwise redirect to viewing
        #UserChallenges should be closed on completion,re-attempts (if allowed)
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = UserChallenge()
        userchallenge.user = request.user
        userchallenge.challenge = challenge
        userchallenge.start()
        userchallenge.save()              
    else:
        if userchallenge.is_complete(): #Complete
            return redirect('challenge-detail', challenge_id=challenge_id)
        
        #if userchallenge.is_new(): #New
        userchallenge.start()
        userchallenge.save()

    questions = challenge.questions.all()[:10] # Returns all questions (NOT random, randomised in generation) 

    
    context = {
        'challenge': challenge, 
        'userchallenge':userchallenge, 
        'questions': questions,

        # List of previous/other challengers on this challenge
        'challengers_done':challenge.userchallenge_set.filter(status=2).order_by('-sq')[0:10],
        'challengers_todo':challenge.userchallenge_set.exclude(status=2).order_by('-sq')[0:10],
        }

    return render_to_response('challenge_do.html', context, context_instance=RequestContext(request))

@login_required
def do_submit(request, challenge_id):

    totals = { 'correct': 0, 'incorrect': 0, 'answered': 0, 'percent': 1 }
    questions = list()

    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # If the user is registered on this concept pull record
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        # Not found
        #FIXME: Should this be another error code? Access denied
        raise Http404

    userchallenge.complete() #Complete (get ourselves a duration value)
    time_to_complete = userchallenge.completed - userchallenge.started
    time_to_complete_each = round( time_to_complete.seconds / challenge.total_questions, 0 )    

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
            # If user has had SQ calculated (default is Null) then store, else use 100
            if request.user.get_profile().sq:
                uqa.user_sq = request.user.get_profile().sq
            else:
                uqa.user_sq = 100
                
            uqa.time_to_complete = time_to_complete_each # Assign point of completion time to the question

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
    if totals['answered'] > 0:
        totals['percent'] = ( 100 * totals['correct'] ) / totals['answered']
    else:
        totals['percent'] = 0

    # Recalculate SQ values for this module/usermodule_set  
    # NOTE: May need to remove this is load too great?
    userchallenge.update_sq()
    userchallenge.save()


    context = {
        'challenge': challenge,
        'userchallenge': userchallenge, 
        'questions': questions, 
        'totals': totals,
        
        # List of previous/other challengers on this challenge
        'challengers_done':challenge.userchallenge_set.filter(status=2).order_by('-sq')[0:10],
        'challengers_todo':challenge.userchallenge_set.exclude(status=2).order_by('-sq')[0:10],
        }

    return render_to_response('challenge_do_submit.html', context, context_instance=RequestContext(request))

@login_required
def generate(request):
    from challenge.utils import generate_user_challenges
    # Generate challenges for the active user, redirect to homepage
    generate_user_challenges(request.user)
    return redirect('home')


