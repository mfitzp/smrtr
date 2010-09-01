from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Smrtr
from challenge.models import *
from network.models import *
from questions.models import *
from package.models import *
from resources.models import *
from challenge.forms import *
from core.http import Http403
# External
from haystack.query import SearchQuerySet


# Get an challenge id and present a page showing detail
# if user is registered on the challenge, provide a additional information
def providers(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    providers = challenge.package_set.all()
    return render_to_response('challenge_providers.html', {'challenge': challenge, 'providers': providers}, context_instance=RequestContext(request))




# CONCEPT VIEWS

# Get an challenge id and present a page showing detail
# if user is registered on the challenge, provide a tailored page
def detail(request, challenge_id):

    challenge = get_object_or_404(Challenge, pk=challenge_id)
    try:
        userchallenge = UserChallenge.objects.get(challenge=challenge, user=request.user)
    except:
        userchallenge = list()

    context = { 'challenge': challenge, 
                'userchallenge': userchallenge, 
                'members': challenge.users.order_by('-userchallenge__sq')[0:12],
                'total_members': challenge.users.count(),                
                # Wall items
                "wall": challenge.wall,
                "wallitems": challenge.wall.wallitem_set.all()
            }

    return render_to_response('challenge_detail.html', context, context_instance=RequestContext(request))

# Register for this challenge
# pass in challengeinstance for context to pull of userchallenge record (specific)
@login_required
def register(request, challenge_id ):

    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == 'POST':
        uc = UserChallenge()
        uc.user = request.user
        
        uc.challenge = challenge
        uc.save()
        
        request.user.message_set.create(
            message=challenge.name + _(u" has been added to your study list"))
                        
        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('challenge-detail', challenge_id=challenge.id)

    return redirect('challenge-detail', challenge_id=challenge.id)
    

    
# Create a new challenge
@login_required
def create(request):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403
                
    if request.POST:
        form = ChallengeForm(request, request.POST, request.FILES)       

        if form.is_valid(): # All validation rules pass
            challenge = form.save()
            # Add the creating user the challenge
            try:
                UserChallenge(user=request.user, challenge=challenge).save()
            except:
                pass
            return redirect(challenge.get_absolute_url()) # Redirect to default view for the challenge
    else:
        form = ChallengeForm(request) # Allow prepopulate  
   
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
        form = ChallengeForm(request, request.POST, request.FILES, instance=challenge)       

        if form.is_valid(): # All validation rules pass
            challenge = form.save()
            return redirect(challenge.get_absolute_url()) # Redirect to default view for the challenge
    else:
        form = ChallengeForm(request, instance=challenge) # Allow prepopulate  
   
    context = { 
        'form': form,
        'challenge': challenge,
    }
    
    return render_to_response("challenge_edit.html", context, context_instance=RequestContext(request))   
  





# Add questions to the challenge
# Presents a search mechanism to find questions (using free text and tags)
# Returned questions can be ticked and added through this interface
# TODO: Provide mechanism for deletion
@login_required
def add_questions(request, challenge_id):
    
    from questions.forms import QuestionSearchForm
    
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    
    # Get usernetwork of the challenge's 'home network'
    # must be a member of the network to add questions
    # additional limitations may be set by the network

    if request.POST.get('addquestion'):
        
        qids = request.POST.getlist('addquestion')
        
        for qid in qids:
            challenge.questions.add( Question.objects.get( pk=qid ) )
            
        # Update total_question count for this challenge
        # used to highlight empty challenges and to exclude them from challenges
        challenge.total_questions = challenge.questions.count()
        challenge.update_statistics()
        challenge.save()
        
        messages.success( request, _(u"%s questions added to %s" % ( len(qids) , challenge.name ) ) )
        
        #if request.POST.get('next'):
            

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q': challenge.name}

    sqs = SearchQuerySet().models(Question)
    #sqs = sqs.load_all_queryset(Question, Question.objects.select_related(depth=1) ) #exclude(challenges=challenge)

    form = QuestionSearchForm(querydata, searchqueryset=sqs, load_all=True )
    results = []
    
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
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'challenge': challenge, 
    }

    return render_to_response('challenge_add_questions.html', context, context_instance=RequestContext(request))    








# Add resources to the challenge
# Presents a search mechanism to find resources (using free text and tags)
# Returned resources can be ticked and added through this interface
# TODO: Provide mechanism for deletion
@login_required
def add_resources(request, challenge_id):
    
    from resources.forms import ResourceSearchForm
    
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    
    # Get usernetwork of the challenge's 'home network'
    # must be a member of the network to add questions
    # additional limitations may be set by the network

    if request.POST.get('addresource'):
        
        rids = request.POST.getlist('addresource')
        
        for rid in rids:
            cr = ChallengeResource( challenge=challenge, resource=Resource.objects.get( pk=rid ) )
            try:
                cr.save()
            except:
                pass
            
        # Update total resources count for this challenge
        # challenge.total_resources = challenge.resource_set.count()
        challenge.total_questions = challenge.resources.count()
        challenge.save()
        messages.success( request, _(u"%s resources added to %s" % ( len(rids) , challenge.name ) ) )
        
        #if request.POST.get('next'):

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q': challenge.name}

    sqs = SearchQuerySet().models(Resource)

    form = ResourceSearchForm(querydata, searchqueryset=sqs, load_all=True )
    results = []
    
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
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'challenge': challenge, 
    }

    return render_to_response('challenge_add_resources.html', context, context_instance=RequestContext(request))    
    
 
def resources(request, challenge_id):
    
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    
    # If the user is registered on this challenge pull record
    try:
        userchallenge = challenge.userchallenge_set.get( user=request.user )
    except:
        userchallenge = list()
        
    resources = Resource.objects.all().filter(challengeresource__challenge=challenge).distinct()
    
    return render_to_response('challenge_resources.html', {'challenge': challenge, 'userchallenge':userchallenge, 'resources': resources}, context_instance=RequestContext(request))



    
    
# Presents a search mechanism to find challenges (and packages) to activate (optionally) (free text and tags)
@login_required
def search( request, 
                    template_name='challenge_search.html',
                    next=None ):
    
    if next is None:
        next = request.GET.get('next')    
    
    from challenge.forms import ChallengeSearchForm
    
    if request.POST.get('addchallenge') or request.POST.get('addpackage'):
        
        cids = request.POST.getlist('addchallenge')
        pids = request.POST.getlist('addpackage')
        
        for cid in cids:
            challenge = Challenge.objects.get(pk=cid)
            userchallenge = UserChallenge( user=request.user, challenge=challenge  )
            try:
                userchallenge.save()
            except:
                messages.warning(request, _(u"You have already activated %s" % challenge.name ) )
            else:
                messages.success(request, _(u"You have activated %s" % challenge.name ) )

        for pid in pids:
            package = Package.objects.get(pk=pid)
            userpackage = UserPackage( user=request.user, package=package  )
            try:
                userpackage.save()
            except:
                messages.warning(request, _(u"You have already activated %s" % package.name ) )
            else:
                messages.success(request, _(u"You have activated %s" % package.name ) )

        if next:
            return redirect( next )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Package, Challenge)
    
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
        
    paginator = Paginator(results, 10)
        
    try:
        page_obj = paginator.page(int(request.GET.get('page', 1)))
    except (ValueError, EmptyPage, InvalidPage): 
        raise Http404("No such page of results!")    
    
    #assert False, dir(list(results)[0])    
    
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
        userchallenge.save()
        
    context = {
        'challenge': challenge, 
        'userchallenge':userchallenge, 
        # List of resources for this challenge's challenges
        'audiovideo': Resource.audiovideo.filter(challenges=challenge),
        'books': Resource.books.filter(challenges=challenge),
        'links': Resource.links.filter(challenges=challenge),
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

    uca = UserChallengeAttempt(user=request.user, challenge=challenge)
    uca.start()
    uca.save()
                
    questions = challenge.questions.all() # Returns all questions (NOT random, randomised in generation) 
    
    context = {
        'challenge': challenge, 
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
    
    try:
        userchallengeattempt = UserChallengeAttempt.objects.filter(challenge=challenge, user=request.user, completed=None )[0]
    except:
        raise Http503
    
    userchallengeattempt.complete()
    
    time_to_complete = userchallengeattempt.started - userchallengeattempt.completed #userchallengeset.completed - userchallengeset.started
    time_to_complete_each = max( 5, time_to_complete.seconds / challenge.total_questions) # Minimum 5 seconds per question
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
                totals['incorrect'] += 1
                userchallenge.current_streak += 0
                uqa.percent_correct = 0
            else:
                totals['correct'] += 1
                userchallenge.current_streak += 1
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
    userchallengeattempt.percent_correct = totals['percent']
    userchallengeattempt.save()
    
    userchallenge.percent_correct = totals['percent']
    userchallenge.total_attempts += 1
    userchallenge.update_focus(last_attempted = userchallenge.completed )
    userchallenge.save()

    try:
        nextchallenge = request.user.userchallenge_set.exclude(challenge__total_questions=0).filter(focus__gt=80).order_by('-focus')[0]
    except:
        nextchallenge = None
##
    challengers = challenge.userchallenge_set.order_by('-percent_correct')

    context = {
        'challenge': challenge,
        'userchallenge': userchallenge, 

        'nextchallenge': nextchallenge,
        
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




