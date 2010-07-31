from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
# Smrtr
from education.models import *
# External
from haystack.query import SearchQuerySet, RelatedSearchQuerySet

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
    
    
    
# Presents a search mechanism to find networks to join (optionally) (free text and tags)
def network_search(request):
    
    from network.forms import NetworkSearchForm
    
    if request.POST.get('addnetwork'):
        
        nids = request.POST.getlist('addnetwork')
        
        for nid in nids:
            network = Network.objects.get(pk=nid)
            usernetwork = UserNetwork( user=request.user, network=network  )
            try:
                usernetwork.save()
            except:
                messages.warning(request, _(u"You are already a member of %s" % network.name ) )
            else:
                messages.success(request, _(u"You have joined %s" % network.name ) )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Network)

    if request.POST:
        querydata = request.POST
    elif request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q':''}
        
    form = NetworkSearchForm(querydata, searchqueryset=sqs, load_all=True )
        
    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search_split() # Returns a list of SearchQuerySets one for each network type
    
    from network.models import TYPE_CHOICES
    
    context = { 
        'form': form,
        'query': query,
        'results': results,
        'TYPE_CHOICES': TYPE_CHOICES,
        'next' : request.GET.get('next'),
    }
    
    return render_to_response('network_search.html', context, context_instance=RequestContext(request))    
    
    
        

