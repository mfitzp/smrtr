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
from core.http import Http403  
# External
from haystack.query import SearchQuerySet, RelatedSearchQuerySet

# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def detail(request, network_id):

    network = get_object_or_404(Network, pk=network_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = network.usernetwork_set.get( user=request.user )
    except:
        usernetwork = list()
        network.challenges_filtered = network.challenges.all().order_by('name')
    else:
        # Generate filter list of challenges with associated user data
        # If user registered attach userchallenge linker and prepend (top list)
        # else append (bottom list)
        network.challenges_filtered = list()
        
        for challenge in network.challenges.all().order_by('name'):
            if challenge in request.user.challenges.all():
                challenge.userchallenge = request.user.userchallenge_set.get( challenge = challenge )
            else:
                pass
            network.challenges_filtered.append(challenge)
             

    context = { 'network': network, 
                'usernetwork': usernetwork, 
                'members': network.members.order_by('-usernetwork__start_date')[0:12],
                'total_members': network.members.count(),                
                "wall": network.wall,
                "wallitems":  network.wall.wallitem_set.all()
              }

    return render_to_response('network_detail.html', context, context_instance=RequestContext(request))



# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
@login_required
def register(request, network_id):

    network = get_object_or_404(Network, pk=network_id)

    if request.POST:
        un = UserNetwork()
        un.user = request.user
        un.network = network
        
        try:
            un.save()
        except:
            request.user.message_set.create(
                message=_(u"You are already a member of ") + network.name)
        else:
            # Write to database 
            request.user.message_set.create(
                message=_(u"You are now a member of ") + network.name)
            if 'success_url' in request.POST:
                return HttpResponseRedirect(request.POST['success_url'])
            else:
                return redirect('network-detail', network_id=network.id)

    return detail(request, network_id)


# Remove a user from the specified network
@login_required
def unregister(request, network_id):

    network = get_object_or_404(Network, pk=network_id)
    usernetwork = get_object_or_404(UserNetwork, network=network, user=request.user)

    if request.method == 'POST':
        usernetwork.delete()

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('network-detail', network_id=network.id)

    return redirect('network-detail', network_id=network.id)


def members(request, network_id):
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
@login_required
def search( request, 
                    template_name='network_search.html',
                    next=None ):
    
    from network.forms import NetworkSearchForm
    
    if request.POST.get('addnetwork'):
        
        nids = request.POST.getlist('addnetwork')
        
        for nid in nids:
            network = Network.objects.get(pk=nid)
            usernetwork = UserNetwork( user=request.user, network=network  )
            usernetwork.save()
            try:
                usernetwork.save()
            except:
                messages.warning(request, _(u"You are already a member of %s" % network.name ) )
            else:
                messages.success(request, _(u"You have joined %s" % network.name ) )
        if next:
            return redirect( next )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Network)

    from profiles.utils import searchqueryset_profile_boost
    sqs = searchqueryset_profile_boost( request, sqs )

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q':' '} #Default search return all
        
    form = NetworkSearchForm(querydata, searchqueryset=sqs, load_all=True )

    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search()[:500]
    
    paginator = Paginator(results, 10)
        
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
    
    
# Set the home network for a user
@login_required
def set_home(request, network_id):
    
    if request.POST:
        network = get_object_or_404(Network, pk=network_id)
        profile = request.user.get_profile()

        profile.network = network
        profile.save()

    return redirect('network-detail', network_id=network.id)    
    
        

