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
from education.models import *
from network.models import *
from questions.models import *
from resources.models import *
from education.forms import *
from core.http import Http403
# External
from haystack.query import SearchQuerySet

# MODULE VIEWS

# Get an topic id and present a page showing detail
# if user is registered on the topic, provide a additional information
def topic_detail(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    
    try:
        # usertopics "you are studying this topic at..."
        usertopic = UserTopic.objects.get(topic=topic, user=request.user)
    except:
        usertopic = list()
        topic.concepts_filtered = topic.concepts.all().order_by('name')
    else:
        # Generate filter list of concepts with associated user data
        topic.concepts_filtered = list()
        
        for concept in topic.concepts.all().order_by('name'):
            if concept in request.user.concepts.all():
                concept.userconcept = request.user.userconcept_set.get( concept = concept )
            else:
                pass
            topic.concepts_filtered.append(concept)
                    

    context = { 'topic': topic, 
                'usertopic': usertopic,
                'members': topic.users.order_by('-usertopic__start_date')[0:12],
                'total_members': topic.users.count(),                
                # Forum items
                "forum": topic.forum,
                "threads": topic.forum.thread_set.all(),
                'next':request.GET.get('next')
              }

    return render_to_response('topic_detail.html', context, context_instance=RequestContext(request) )


# Get an insititution id and present a page showing detail
# if user is registered at the topic, provide a tailored page
@login_required
def topic_register(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)

    if request.method == 'POST':
        um = UserTopic()
        um.user = request.user
        
        # Find user record for parent network, must be registered on the network to register for topic
        # try:
            # FIXME: Note this is trying only to check if member of topics 'home' network not any it may have been assigned to
        #    usernetwork = request.user.usernetwork_set.get(network = topic.network)
        # except:
            # Error
        #    pass

        um.topic = topic
        um.save()
        request.user.message_set.create(
        message=_(u"You are now studying ") + topic.name)

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return topic_detail(request, topic_id)

    return topic_detail(request, topic_id)


# Get an topic id and present a page showing detail
# if user is registered on the topic, provide a additional information
def topic_providers(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    providers = topic.networks.all()
    return render_to_response('topic_providers.html', {'topic': topic, 'providers': providers}, context_instance=RequestContext(request))


# Get an topic id and present a page showing detail
# if user is registered on the topic, provide a additional information
def concept_providers(request, concept_id):
    concept = get_object_or_404(Concept, pk=concept_id)
    providers = concept.topic_set.all()
    return render_to_response('concept_providers.html', {'concept': concept, 'providers': providers}, context_instance=RequestContext(request))




# CONCEPT VIEWS

# Get an concept id and present a page showing detail
# if user is registered on the concept, provide a tailored page
def concept_detail(request, concept_id):

    concept = get_object_or_404(Concept, pk=concept_id)
    try:
        userconcept = UserConcept.objects.get(concept=concept, user=request.user)
    except:
        userconcept = list()

    context = { 'concept': concept, 
                'userconcept': userconcept, 
                'members': concept.users.order_by('-userconcept__start_date')[0:12],
                'total_members': concept.users.count(),                
                # Forum items
                "forum": concept.forum,
                "threads": concept.forum.thread_set.all()
            }

    return render_to_response('concept_detail.html', context, context_instance=RequestContext(request))

# Register for this concept
# pass in topicinstance for context to pull of usertopic record (specific)
@login_required
def concept_register(request, concept_id ):

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
def concept_create(request):

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
def concept_edit(request, concept_id):

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
  



# Create a new topic
@login_required
def topic_create(request):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403
                
    if request.POST:
        form = TopicForm(request, request.POST)       

        if form.is_valid(): # All validation rules pass
            topic = form.save()
            return redirect(topic.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = TopicForm(request, request.GET) # Allow prepopulate  
   
    context = { 
        'form': form,
        'topic': None,
    }
    
    return render_to_response("topic_edit.html", context, context_instance=RequestContext(request)) 
    
    

# Edit a topic
@login_required
def topic_edit(request, topic_id):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403

    topic = get_object_or_404(Topic, pk=topic_id)
                    
    if request.POST:
        form = TopicForm(request, request.POST, instance=topic)       

        if form.is_valid(): # All validation rules pass
            topic = form.save()
            return redirect(topic.get_absolute_url()) # Redirect to default view for the concept
    else:
        form = TopicForm(request, instance=topic) # Allow prepopulate  
   
    context = { 
        'form': form,
        'topic': topic,
    }
    
    return render_to_response("topic_edit.html", context, context_instance=RequestContext(request))   
  




# Add questions to the concept
# Presents a search mechanism to find questions (using free text and tags)
# Returned questions can be ticked and added through this interface
# TODO: Provide mechanism for deletion
@login_required
def concept_add_questions(request, concept_id):
    
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
def concept_add_resources(request, concept_id):
    
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
    
 
def concept_resources(request, concept_id):
    
    concept = get_object_or_404(Concept, pk=concept_id)
    
    # If the user is registered on this topic pull record
    try:
        userconcept = concept.userconcept_set.get( user=request.user )
    except:
        userconcept = list()
        
    resources = Resource.objects.all().filter(conceptresource__concept=concept).distinct()
    
    return render_to_response('concept_resources.html', {'concept': concept, 'userconcept':userconcept, 'resources': resources}, context_instance=RequestContext(request))














    
    
# Presents a search mechanism to find topics to activate (optionally) (free text and tags)
@login_required
def topic_search( request, 
                    template_name='topic_search.html',
                    next=None ):
    
    from education.forms import TopicSearchForm
    
    if request.POST.get('addtopic'):
        
        mids = request.POST.getlist('addtopic')
        
        for mid in mids:
            topic = Topic.objects.get(pk=mid)
            usertopic = UserTopic( user=request.user, topic=topic  )
            try:
                usertopic.save()
            except:
                messages.warning(request, _(u"You have already activated %s" % topic.name ) )
            else:
                messages.success(request, _(u"You have activated %s" % topic.name ) )
        if next:
            return redirect( next )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Topic)
    
    from network.utils import searchqueryset_usernetwork_boost
    sqs = searchqueryset_usernetwork_boost( request, sqs )    

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q':' '} #Default search return all
        
    form = TopicSearchForm(querydata, searchqueryset=sqs, load_all=True )

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


