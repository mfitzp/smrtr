from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
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
            userchallenge = UserChallenge()
            userchallenge.user = request.user
            userchallenge.challenge = challenge
            userchallenge.update_sq()
            userchallenge.save()
            
            return HttpResponseRedirect( reverse('challenge-do',kwargs={'challenge_id':challenge.id} ) ) # Redirect to challenge_do for this challenge
    
    else:
        prefill = {}
        prefillq = ['name','description','targetsq','total_questions']
        
        for src in prefillq:
            if request.GET.get(src):
                prefill[src] = request.GET.get(src)
        
        if request.GET.getlist('concepts'):
            prefill['concepts'] = request.GET.getlist('concepts')
        
            if 'name' not in prefill:
                name = list()
                # Build suggested name from concept lists
                for concept in prefill['concepts']:
                    
                    try:
                        c = Concept.objects.get(pk=concept)
                    except:
                        pass
                    else:
                        name.append( c.name )
                        
                prefill['name'] = ', '  .join( name )
        
        if 'targetsq' not in prefill:
            prefill['targetsq'] = request.user.get_profile().sq # If not set, find user's SQ and preset
        
        # TODO: Prefill concepts from csv list on query url
        # TODO: Prefill name/description (if not set yet) based on contents of concept list
        
        form = ChallengeForm(initial=prefill, instance=challenge) 
        
        # Provide concept-possibilities (from user's own lists)
        form.fields['concepts'].queryset = Concept.objects.filter(userconcept__user=request.user)

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

    context = {
        'challenge': challenge,
        'userchallenge':userchallenge,
        
        # List of previous/other challengers on this challenge
        'challengers_done':challenge.userchallenge_set.filter(status=2).order_by('-sq')[0:10],
        'challengers_todo':challenge.userchallenge_set.exclude(status=2).order_by('-sq')[0:10],
        }

    return render_to_response('challenge_view.html', context, context_instance=RequestContext(request))




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
        userchallenge.update_sq() # Initial value from previous answers to included questions
        userchallenge.status = 1 # Active
        userchallenge.save()              
    else:
        if userchallenge.status == 2: #Complete
            return redirect('challenge-detail', challenge_id=challenge_id)
        
        if userchallenge.status == 0: #New
            userchallenge.status = 1
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
            uqa.usq = request.user.get_profile().sq

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
    userchallenge.status = 2 #Complete
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


def generate(request):
    from challenge.utils import generate_user_challenges
    # Generate challenges for the active user, redirect to homepage
    generate_user_challenges(request.user)
    return HttpResponseRedirect('/')


