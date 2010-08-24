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
from concept.models import *
from network.models import *
from questions.models import *
from resources.models import *
from concept.forms import *
from core.http import Http403
# External
from haystack.query import SearchQuerySet


# Get an challenge id and present a page showing detail
# if user is registered on the challenge, provide a additional information
def providers(request, concept_id):
    concept = get_object_or_404(Concept, pk=concept_id)
    providers = concept.challenge_set.all()
    return render_to_response('concept_providers.html', {'concept': concept, 'providers': providers}, context_instance=RequestContext(request))




# CONCEPT VIEWS

# Get an concept id and present a page showing detail
# if user is registered on the concept, provide a tailored page
def detail(request, concept_id):

    concept = get_object_or_404(Concept, pk=concept_id)
    try:
        userconcept = UserConcept.objects.get(concept=concept, user=request.user)
    except:
        userconcept = list()

    context = { 'concept': concept, 
                'userconcept': userconcept, 
                'members': concept.users.order_by('-userconcept__start_date')[0:12],
                'total_members': concept.users.count(),                
                # Wall items
                "wall": concept.wall,
                "wallitems": concept.wall.wallitem_set.all()
            }

    return render_to_response('concept_detail.html', context, context_instance=RequestContext(request))

# Register for this concept
# pass in challengeinstance for context to pull of userchallenge record (specific)
@login_required
def register(request, concept_id ):

    concept = get_object_or_404(Concept, pk=concept_id)

    if request.method == 'POST':
        uc = UserConcept()
        uc.user = request.user
        
        uc.concept = concept
        uc.save()
        
        request.user.message_set.create(
            message=concept.name + _(u" has been added to your study list"))
                        
        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return concept_detail(request, concept_id)

    return concept_detail(request, concept_id)

    

    

# Create a new concept
@login_required
def create(request):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403
                
    if request.POST:
        form = ConceptForm(request, request.POST)       

        if form.is_valid(): # All validation rules pass
            concept = form.save()
            return redirect(concept.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = ConceptForm(request, request.GET) # Allow prepopulate  
   
    context = { 
        'form': form,
        'concept': None,
    }
    
    return render_to_response("concept_edit.html", context, context_instance=RequestContext(request)) 
    
    

# Edit a concept
@login_required
def edit(request, concept_id):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403

    concept = get_object_or_404(Concept, pk=concept_id)
                    
    if request.POST:
        form = ConceptForm(request, request.POST, instance=concept)       

        if form.is_valid(): # All validation rules pass
            concept = form.save()
            return redirect(concept.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = ConceptForm(request, instance=concept) # Allow prepopulate  
   
    context = { 
        'form': form,
        'concept': concept,
    }
    
    return render_to_response("concept_edit.html", context, context_instance=RequestContext(request))   
  





# Add questions to the concept
# Presents a search mechanism to find questions (using free text and tags)
# Returned questions can be ticked and added through this interface
# TODO: Provide mechanism for deletion
@login_required
def add_questions(request, concept_id):
    
    from questions.forms import QuestionSearchForm
    
    concept = get_object_or_404(Concept, pk=concept_id)
    
    # Get usernetwork of the concept's 'home network'
    # must be a member of the network to add questions
    # additional limitations may be set by the network

    if request.POST.get('addquestion'):
        
        qids = request.POST.getlist('addquestion')
        
        for qid in qids:
            concept.question_set.add( Question.objects.get( pk=qid ) )
            
        # Update total_question count for this concept
        # used to highlight empty concepts and to exclude them from challenges
        concept.total_questions = concept.question_set.count()
        concept.save()
        
        messages.success( request, _(u"%s questions added to %s" % ( len(qids) , concept.name ) ) )
        
        #if request.POST.get('next'):
            

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q': concept.name}

    sqs = SearchQuerySet().models(Question)
    #sqs = sqs.load_all_queryset(Question, Question.objects.select_related(depth=1) ) #exclude(concepts=concept)

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
        'concept': concept, 
    }

    return render_to_response('concept_add_questions.html', context, context_instance=RequestContext(request))    








# Add resources to the concept
# Presents a search mechanism to find resources (using free text and tags)
# Returned resources can be ticked and added through this interface
# TODO: Provide mechanism for deletion
@login_required
def add_resources(request, concept_id):
    
    from resources.forms import ResourceSearchForm
    
    concept = get_object_or_404(Concept, pk=concept_id)
    
    # Get usernetwork of the concept's 'home network'
    # must be a member of the network to add questions
    # additional limitations may be set by the network

    if request.POST.get('addresource'):
        
        rids = request.POST.getlist('addresource')
        
        for rid in rids:
            cr = ConceptResource( concept=concept, resource=Resource.objects.get( pk=rid ) )
            try:
                cr.save()
            except:
                pass
            
        # Update total resources count for this concept
        # concept.total_resources = concept.resource_set.count()
        concept.save()
        messages.success( request, _(u"%s resources added to %s" % ( len(rids) , concept.name ) ) )
        
        #if request.POST.get('next'):

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q': concept.name}

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
        'concept': concept, 
    }

    return render_to_response('concept_add_resources.html', context, context_instance=RequestContext(request))    
    
 
def resources(request, concept_id):
    
    concept = get_object_or_404(Concept, pk=concept_id)
    
    # If the user is registered on this challenge pull record
    try:
        userconcept = concept.userconcept_set.get( user=request.user )
    except:
        userconcept = list()
        
    resources = Resource.objects.all().filter(conceptresource__concept=concept).distinct()
    
    return render_to_response('concept_resources.html', {'concept': concept, 'userconcept':userconcept, 'resources': resources}, context_instance=RequestContext(request))














    
    
# Presents a search mechanism to find challenges to activate (optionally) (free text and tags)
@login_required
def challenge_search( request, 
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


