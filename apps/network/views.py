from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Spenglr
from education.models import *

# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_detail(request, network_id):


    network = get_object_or_404(Network, pk=network_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = network.usernetwork_set.get( user=request.user )
    except:
        usernetwork = list()
        network.modules_filtered = network.modules.all().order_by('name')
    else:
        # Generate filter list of modules with associated user data
        # If user registered attach usermodule linker and prepend (top list)
        # else append (bottom list)
        network.modules_filtered = list()
        
        for module in network.modules.all().order_by('name'):
            if module in request.user.modules.all():
                module.usermodule = request.user.usermodule_set.get( module = module )
            else:
                pass
            network.modules_filtered.append(module)
             

    context = { 'network': network, 
                'usernetwork': usernetwork, 
                'members': network.members.order_by('-usernetwork__start_date')[0:12],
                'total_members': network.members.count(),                
                "forum": network.forum,
                "threads": network.forum.thread_set.all()
              }

    return render_to_response('network_detail.html', context, context_instance=RequestContext(request))



# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_register(request, network_id):

    network = get_object_or_404(Network, pk=network_id)

    if request.POST:
        un = UserNetwork()
        un.user = request.user
        
        try:
            un.network = network
            
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, un
            pass

        else:
            # Write to database 
            un.save()
            request.user.message_set.create(
                message=_(u"You are now a member of ") + network.name)
            if 'success_url' in request.POST:
                return HttpResponseRedirect(request.POST['success_url'])
            else:
                return network_detail(request, network_id)

    return render_to_response('network_register.html', {'network': network }, context_instance=RequestContext(request))



def network_members(request, network_id):
    network = get_object_or_404(Network, pk=network_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = network.usernetwork_set.get( user=request.user )
    except:
        usernetwork = None

    context = { 'network': network, 
                'usernetwork': usernetwork, 
                'members': network.members.order_by('-usernetwork__start_date'),
                'total_members': network.members.count(),                      
              }

    return render_to_response('network_members.html', context, context_instance=RequestContext(request))
    
    
    
# Presents a search mechanism to find networks (free text and tags)
def network_search(request, concept_id):
    
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
    
    
        

