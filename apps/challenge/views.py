# Django
from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.template.loader import render_to_string
from django.utils import simplejson as json
# Smrtr
from challenge.models import *
from challenge.forms import *

from network.models import *
from questions.models import *
from resources.models import *
from core.http import Http403
# External
from haystack.query import SearchQuerySet

# MODULE VIEWS

# Get an challenge id and present a page showing detail
# if user is registered on the challenge, provide a additional information
def detail(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    
    try:
        # userchallenges "you are studying this challenge at..."
        userchallenge = UserChallenge.objects.get(challenge=challenge, user=request.user)
    except:
        userchallenge = None

    # Generate filter list of concepts with associated user data
    challenge.concepts_filtered = list()
    
    if request.user.is_authenticated:
        for concept in challenge.concepts.all().order_by('name'):
            if concept in request.user.concepts.all():
                concept.userconcept = request.user.userconcept_set.get( concept = concept )
            else:
                pass
            challenge.concepts_filtered.append(concept)
    else:
        challenge.concepts_filtered = challenge.concepts.all().order_by('name')
                    

    context = { 'challenge': challenge, 
                'userchallenge': userchallenge,
                'userchallenges': challenge.userchallenge_set.order_by('-sq')[0:12],
                'total_members': challenge.users.count(),                
                # Wall items
                "wall": challenge.wall,
                "wallitems": challenge.wall.wallitem_set.all(),
                'next':request.GET.get('next')
              }

    return render_to_response('challenge_detail.html', context, context_instance=RequestContext(request) )


@login_required
def register(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == 'POST':
        uc = UserChallenge()
        uc.user = request.user
        uc.challenge = challenge
        uc.save()

        request.user.message_set.create(
        message=_(u"You are now studying ") + challenge.name)

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('challenge-detail', challenge_id=challenge.id)

    return redirect('challenge-detail', challenge_id=challenge.id)

# Remove a user from the specified challenge
@login_required
def unregister(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    userchallenge = get_object_or_404(UserChallenge, challenge=challenge, user=request.user)

    if request.method == 'POST':
        userchallenge.delete()

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('challenge-detail', challenge_id=challenge.id)

    return redirect('challenge-detail', challenge_id=challenge.id)



# Get an challenge id and present a page showing detail
# if user is registered on the challenge, provide a additional information
def providers(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    providers = challenge.networks.all()
    return render_to_response('challenge_providers.html', {'challenge': challenge, 'providers': providers}, context_instance=RequestContext(request))




# Create a new challenge
@login_required
def create(request):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403
                
    if request.POST:
        form = ChallengeForm(request, request.POST)       

        if form.is_valid(): # All validation rules pass
            challenge = form.save()
            return redirect(challenge.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = ChallengeForm(request, request.GET) # Allow prepopulate  
   
    context = { 
        'form': form,
        'challenge': None,
    }
    
    return render_to_response("challenge_edit.html", context, context_instance=RequestContext(request)) 
    
    

# Edit a challenge
@login_required
def edit(request, challenge_id):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403

    challenge = get_object_or_404(Challenge, pk=challenge_id)
                    
    if request.POST:
        form = ChallengeForm(request, request.POST, instance=challenge)       

        if form.is_valid(): # All validation rules pass
            challenge = form.save()
            return redirect(challenge.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = ChallengeForm(request, instance=challenge) # Allow prepopulate  
   
    context = { 
        'form': form,
        'challenge': challenge,
    }
    
    return render_to_response("challenge_edit.html", context, context_instance=RequestContext(request))   
  
   
    
# Presents a search mechanism to find challenges to activate (optionally) (free text and tags)
@login_required
def search( request, 
                    template_name='challenge_search.html',
                    next=None ):
    
    from challenge.forms import ChallengeSearchForm
    
    if request.POST.get('addchallenge'):
        
        mids = request.POST.getlist('addchallenge')
        
        for mid in mids:
            challenge = Challenge.objects.get(pk=mid)
            userchallenge = UserChallenge( user=request.user, challenge=challenge  )
            try:
                userchallenge.save()
            except:
                messages.warning(request, _(u"You have already activated %s" % challenge.name ) )
            else:
                messages.success(request, _(u"You have activated %s" % challenge.name ) )
        if next:
            return redirect( next )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Challenge)
    
    from network.utils import searchqueryset_usernetwork_boost
    sqs = searchqueryset_usernetwork_boost( request, sqs )    

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q':' '} #Default search return all
        
    form = ChallengeSearchForm(querydata, searchqueryset=sqs, load_all=True )

    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search()
        
    paginator = Paginator(list(results), 10)
        
    try:
        page_obj = paginator.page(int(request.GET.get('page', 1)))
    except (ValueError, EmptyPage, InvalidPage): 
        raise Http404("No such page of results!")    
        
    
    context = { 
        'form': form,
        'query': query,
        'results': results,
        'next' : next,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))    









@login_required
def prepare(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = UserChallenge()
        userchallenge.user = request.user
        userchallenge.challenge = challenge
        # A challengeset should be generated automatically on save and set
        userchallenge.save()
        
    challengeset = userchallenge.challengeset

    if userchallenge.challengeset is None:
        # Something is wrong, we can't get a challengeset for this user, redirect to challenge page
        return redirect('challenge-detail', challenge_id=challenge_id)
        
    context = {
        'challenge': challenge, 
        'challengeset': userchallenge.challengeset, 
        'userchallenge':userchallenge, 
        # List of resources for this challenge's concepts
        'audiovideo': Resource.audiovideo.filter(concepts__challengeset=challengeset),
        'books': Resource.books.filter(concepts__challengeset=challengeset),
        'links': Resource.links.filter(concepts__challengeset=challengeset),
        }

    return render_to_response('challenge_prepare.html', context, context_instance=RequestContext(request))



@login_required
def do(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)

    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = UserChallenge()
        userchallenge.user = request.user
        userchallenge.challenge = challenge
        # A challengeset should be generated automatically on save and set
        userchallenge.save()
        
    challengeset = userchallenge.challengeset

    if userchallenge.challengeset is None:
        # Something is wrong, we can't get a challengeset for this user, redirect to challenge page
        return redirect('challenge-detail', challenge_id=challenge_id)
    
    try:
        UserChallengeSet(user=request.user, challengeset=challengeset).save()
    except:
        userchallengeset = UserChallengeSet.objects.get(user=request.user, challengeset=challengeset)
        if userchallengeset.completed:
            return redirect('challenge-detail', challenge_id=challenge_id)
        # else has been started but failed for some reason (Continue)
        
    questions = challengeset.questions.all()[:10] # Returns all questions (NOT random, randomised in generation) 
    
    context = {
        'challenge': challenge, 
        'challengeset': userchallenge.challengeset, 
        'userchallenge':userchallenge, 
        'questions': questions,
        }

    return render_to_response('challenge_do.html', context, context_instance=RequestContext(request))

@login_required
def do_submit(request, challenge_id):

    totals = { 'correct': 0, 'incorrect': 0, 'answered': 0, 'percent': 1 }
    questions = list()

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    userchallenge = get_object_or_404(UserChallenge, challenge=challenge, user=request.user )
    challengeset = userchallenge.challengeset

    userchallengeset = get_object_or_404(UserChallengeSet, challengeset=challengeset, user=request.user )
    userchallengeset.complete()

    time_to_complete = userchallengeset.completed - userchallengeset.started
    time_to_complete_each = max( 5, time_to_complete.seconds / challengeset.total_questions) # Minimum 5 seconds per question
    time_to_complete_each = round( time_to_complete_each , 0 ) # Remove decimals
    
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

    # Recalculate SQ values for this challenge/userchallenge_set  
    # NOTE: May need to remove this is load too great?
    # userchallengeset.update_sq()
    userchallengeset.percent_correct = totals['percent']
    userchallengeset.save()

    # Update concept statistics and focus
    for userconcept in UserConcept.objects.filter(concept__challengeset=challengeset):
        userconcept.update_statistics()
        # Update SQ here?
        userconcept.update_focus(last_attempted = userchallengeset.completed ) # Pass in now to save the last_attempted lookup
        
    # We've completed this one, so get a new one ready for next time    
    userchallenge.generate_challengeset()

    # Update the userchallenge statistics
    userchallenge.update_statistics()
    userchallenge.save()

    challengers = challengeset.userchallengeset_set.order_by('-percent_correct')

    context = {
        'challenge': challenge,
        'userchallenge': userchallenge, 

        'challengeset': challengeset,
        'userchallengeset': userchallengeset,
        
        'challengers':challengers,

        'questions': questions, 
        'totals': totals,
        
        # List of previous/other challengers on this challenge
        #'challengers_done':challenge.userchallenge_set.filter(status=2).order_by('-sq')[0:10],
        #'challengers_todo':challenge.userchallenge_set.exclude(status=2).order_by('-sq')[0:10],
        
        
        # Wall
        "wall": challenge.wall,
        "wallitems": challenge.wall.wallitem_set.all(),        
        }

    return render_to_response('challenge_do_submit.html', context, context_instance=RequestContext(request))



@login_required
def newset(request, challenge_id):

    if request.POST:
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        userchallenge = get_object_or_404(UserChallenge, challenge=challenge, user=request.user)

        userchallenge.generate_challengeset(exclude_current_challengeset=True)
        userchallenge.save()
            
        next = request.GET.get('next')

        if next:
            return redirect(next)
        else:
            return redirect('home')
        
@login_required
def newset_ajax(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    userchallenge = get_object_or_404(UserChallenge, challenge=challenge, user=request.user)
    userchallenge.generate_challengeset(exclude_current_challengeset=True)
    userchallenge.save()

    result = { 
        'id':challenge_id,
        'content':render_to_string('_challengeset_meta.html', { 'challengeset':userchallenge.challengeset, 'userchallenge':userchallenge } ) 
        }       

    response = HttpResponse()
    json.dump(result, response)
    
    return response



