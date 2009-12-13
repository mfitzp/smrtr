from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Spenglr
from education.models import *
# External
from wall.forms import WallItemForm

# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_detail(request, network_id):


    network = get_object_or_404(Network, pk=network_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = network.usernetwork_set.get( user=request.user )
    except:
        usernetwork = list()
        network.coursei_filtered = network.courseinstance_set.all().order_by('course__name')
    else:
        # Generate filter list of modules with associated user data
        # If user registered attach usermodule linker and prepend (top list)
        # else append (bottom list)
        network.coursei_filtered = list()
    
        for coursei in network.courseinstance_set.all().order_by('course__name'):
            if coursei in request.user.courses.all():
                pass
            else:
                network.coursei_filtered.append(coursei)

    context = { 'network': network, 
                'usernetwork': usernetwork, 
                'members': network.members.all(),
                "wall": network.wall,
                "wallitems": network.wall.wallitem_set.select_related(),
                "wallform": WallItemForm()
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
            return HttpResponseRedirect(reverse('core.views.index'))

    return render_to_response('network_register.html', {'network': network }, context_instance=RequestContext(request))


