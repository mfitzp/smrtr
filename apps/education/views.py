from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
# Spenglr
from education.models import *
from network.models import *
from questions.models import *
# External
from wall.forms import WallItemForm
from haystack.query import SearchQuerySet

# MODULE VIEWS

# Get an module id and present a page showing detail
# if user is registered on the module, provide a additional information
def module_detail(request, module_id):

    module = get_object_or_404(Module, pk=module_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    
    try:
        # usermodules "you are studying this module at..."
        usermodule = UserModule.objects.get(module=module, user=request.user)
    except:
        usermodule = list()
        module.concepts_filtered = module.concepts.all().order_by('name')
    else:
        # Generate filter list of concepts with associated user data
        module.concepts_filtered = list()
        
        for concept in module.concepts.all().order_by('name'):
            if concept in request.user.concepts.all():
                concept.userconcept = request.user.userconcept_set.get( concept = concept )
            else:
                pass
            module.concepts_filtered.append(concept)
                    

    context = { 'module': module, 
                'usermodule': usermodule,
                'members': module.members.order_by('-usermodule__start_date'),
                # Forum items
                "forum": module.forum,
                "threads": module.forum.thread_set.all()
              }

    return render_to_response('module_detail.html', context, context_instance=RequestContext(request) )


# Get an insititution id and present a page showing detail
# if user is registered at the module, provide a tailored page
def module_register(request, module_id):

    module = get_object_or_404(Module, pk=module_id)

    if request.method == 'POST':
        um = UserModule()
        um.user = request.user
        
        # Find user record for parent network, must be registered on the network to register for module
        try:
            # FIXME: Note this is trying only to check if member of modules 'home' network not any it may have been assigned to
            usernetwork = request.user.usernetwork_set.get(network = module.network)
        except:
            assert False, module

        try:
            um.module = module
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, um
            pass

        else:
            # Write to database 
            # um.usernetwork = usernetwork
            um.save()
            
            # Automatically activate all concepts on this module
            # FIXME: Move this out to helper util function (same as for above)
            
            #for concept in module.concepts.all():
            #    try:
            #        uc = UserConcept()    
            #        uc.user = request.user
            #        uc.concept = concept
            #        uc.save()
            #    except:
            #        pass

            if 'success_url' in request.POST:
                return HttpResponseRedirect(request.POST['success_url'])
            else:
                return module_detail(request, module_id)

    return module_detail(request, module_id)


# Get an module id and present a page showing detail
# if user is registered on the module, provide a additional information
def module_detail_providers(request, module_id):

    module = get_object_or_404(Course, pk=module_id)

    # usermodules "you are studying this module at..."
    usermodules = UserCourse.objects.filter(modulei__module=module)

    return render_to_response('module_detail.html', {'module': module, 'usermodules': usermodules}, context_instance=RequestContext(request))







# CONCEPT VIEWS

# Get an concept id and present a page showing detail
# if user is registered on the concept, provide a tailored page
def concept_detail(request, concept_id):

    concept = get_object_or_404(Concept, pk=concept_id)

    # userconcepts "you are studying this concept on these modules..."
    try:
        userconcept = UserConcept.objects.get(concept=concept, user=request.user)
    except:
        userconcept = list()

    #members=concept.#User.objects.filter(userconcept__concepti__concept=concept)

    context = { 'concept': concept, 
                'userconcept': userconcept, 
                'members': concept.members.order_by('-userconcept__start_date'),
                # Forum items
                "forum": concept.forum,
                "threads": concept.forum.thread_set.all()
            }

    return render_to_response('concept_detail.html', context, context_instance=RequestContext(request))

# Register for this concept
# pass in moduleinstance for context to pull of usermodule record (specific)
def concept_register(request, concept_id ):

    concept = get_object_or_404(Concept, pk=concept_id)

    if request.method == 'POST':
        uc = UserConcept()
        uc.user = request.user
        
        try:
            uc.concept = concept
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, uc
            pass

        else:
            # Write to database 
            # um.usernetwork = usernetwork
            uc.save()
            if 'success_url' in request.POST:
                return HttpResponseRedirect(request.POST['success_url'])
            else:
                return concept_detail(request, concept_id)

    return concept_detail(request, concept_id)

# Add questions to the concept
# Presents a search mechanism to find questions (using free text and tags)
# Returned questions can be ticked and added through this interface
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
            

    query = ''
    results = []
    
    searchqueryset = SearchQuerySet().models(Question)

    if request.GET.get('q'):
        form = QuestionSearchForm(request.GET, searchqueryset=searchqueryset, load_all=True )
        
    else:
        form = QuestionSearchForm({'q':concept.name}, searchqueryset=searchqueryset, load_all=True )
        
    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search()
        
    paginator = Paginator(results, 10)
        
    try:
        page_obj = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("No such page of results!")    

    context = { 
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'concept': concept, 
    }
    
    return render_to_response('concept_add_questions.html', context, context_instance=RequestContext(request))    
    
    
    
    
    
    


def concept_resources(request, concept_id):
    
    concept = get_object_or_404(Concept, pk=concept_id)
    
    # If the user is registered on this module pull record
    try:
        userconcept = concept.userconcept_set.get( user=request.user )
    except:
        userconcept = list()
        
    resources = Resource.objects.all().filter(conceptresource__concept=concept).distinct()
    
    return render_to_response('concept_resources.html', {'concept': concept, 'userconcept':userconcept, 'resources': resources}, context_instance=RequestContext(request))
            
