from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.education.models import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_detail(request, network_id):

    network = get_object_or_404(Network, pk=network_id)
    memberships = network.memberships()

    # If the user is registered at this network, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = memberships.get( user=request.user )
    except:
        usernetwork = list()

    network.courses_filtered = list()

    # Find all courses being offered by this network
    for course in network.courses_offered.all():
        if course in request.user.courses.all():
            pass
        else:
            network.courses_filtered.append( course )

    # Find all courses owned by this network
    for course in network.course_set.all():
        if course in request.user.courses.all():
            pass
        else:
            network.courses_filtered.append( course )


    return render_to_response('network/network_detail.html', {'network': network, 'usernetwork': usernetwork, 'memberships': memberships})



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
            return HttpResponseRedirect(reverse('spenglr.core.views.index'))

    return render_to_response('network/network_register.html', {'network': network })


