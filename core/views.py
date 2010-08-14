from django.conf import settings
from django import http
from django.template import Context, RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg

# External
from notification.models import Notice
# Smrtr
from network.models import Network
from education.models import Module, UserModule, Concept
from challenge.models import Challenge
from core.forms import LoginForm
from discuss.models import *


def home(request):

    if request.user.is_authenticated():

        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()

        usermodules = request.user.usermodule_set.all()
        
        #userconcepts = request.user.userconcept_set.filter(focus__gt=0).order_by('-focus')

        userchallenges = request.user.userchallenge_set.filter(status__lt=2).order_by('status')[0:5]
        userchallengescomplete = request.user.userchallenge_set.filter(status__exact=2)[0:3]
        # If no userchallenges available, attempt to populate
        # FIXME: This is going to fire on every dashboard load until the user has some challenge
        # it's relatively quick/smart but still clunky. An 'event' trigger mechanism whereby
        # this is called when new modules are activated would be preferable (adding this directly
        # to the education app creates an unwanted dependency).
        if not userchallenges:
            if usermodules: # Only generate if there are modules available
                from challenge.utils import generate_userchallenges
                generate_userchallenges(request.user)
                userchallenges = request.user.userchallenge_set.filter(status__lt=2).order_by('status')[0:5]
        
        # Flag True/False whether challenges exist at all for this user
        userchallengesexist = ( userchallenges.count() + userchallengescomplete.count() ) > 0
        
        # Get next activated concepts (available by modules reverse SQ), retrieving 5
        # Gets all concepts that are available (on user's modules) but not active
        # Later limit by 'dependencies on individual entries'
        # suggestconcepts = Concept.objects.exclude(userconcept__user=request.user).filter(module__usermodule__user=request.user).order_by('-sq')[0:3]
        suggestmodules = Module.objects.exclude(usermodule__user=request.user).filter(network__usernetwork__user=request.user).order_by('-sq')

        notices = Notice.objects.notices_for(request.user, on_site=True)

        # Top users for front page (will want network top users later also, perhaps)
        # Put this on another page (stats, ranking, etc.)
        # topusers = User.objects.order_by('-userprofile__sq')[0:5]

        # Front page wallitems (wi) combine the user's accessible wall posts from 
        # user profile, networks, courses and modules (& friends later)
        
        # Posts to SYSTEM wall *ALWAYS* appear
        threads = Forum.objects.get(pk=1).thread_set.select_related()
        
        # TODO: All the following need some mechanism to filter, reduce the number shown
        # Like +1, Comment +1 or +2
        # Personal rating/comment more weight than others (*2) e.g 
        
        # NOTE: Can  weight each network, module, concept by limiting
        # the max number of posts got from each at this point,
        # e.g. pull 5 from each concept, 10 from each network will *2 favour network posts
        
        # Posts on user's networks, courses, modules
        for un in usernetworks:
            threads = threads | un.network.forum.thread_set.select_related()
          
        # These need to be limited to active only
        for um in usermodules:
            threads = threads | um.module.forum.thread_set.select_related()
                    
        # Filter out to show only *other* users - may not want this as comments/etc. on user's 
        # own posts will be missed? Depends on the profile/dashboard interaction - future
        # No __ne filter here?! Use combination of lt, gt for result
        # wi = wi.filter(Q(author__id__lt=request.user.id) | Q(author__id__gt=request.user.id))

        # TODO: Resulting queryset must be filtered to only show those users actually on
        # the user's own networks (option configuration switching here)
        # wi = wi.filter(author=request.user)
        #wi = wi.filter(author__usernetwork__network__usernetwork__user=request.user).distinct()

        i = RequestContext(request, {
            'usernetworks': usernetworks,
            'usermodules': usermodules,
    #            'userconcepts': userconcepts,
            # Suggest
    #            'suggestconcepts' : suggestconcepts,
            'suggestmodules' : suggestmodules,
            # Challenges
            'userchallengesexist': userchallengesexist,
            'userchallenges': userchallenges,
            'userchallengescomplete': userchallengescomplete,
            
            # Notifications
            #'notices' : Notice.objects.notices_for(request.user, on_site=True)[0:3],            
            
            # Combined threads available to this user, limited to 10 max
            'threads': threads[0:10],
        })
        
        return render_to_response('dashboard.html', i, context_instance=RequestContext(request))
        
    else:
        # Not logged in
        return welcome(request)



def welcome(request):

    from django.contrib.auth.forms import AuthenticationForm

    topusers = User.objects.order_by('-userprofile__sq')[0:5]
    topnetworks = Network.objects.annotate(num_users=Count('usernetwork')).order_by('-num_users')[0:10]
    topchallenges = Challenge.objects.annotate(num_users=Count('userchallenge')).order_by('-num_users')[0:5]
    
    authentication_form = AuthenticationForm

    if request.GET.get('next') == '/':
        is_home = True
    else:
        is_home = False
    
    context = RequestContext(request, {
            'form' : authentication_form(request),
            'is_home' : request.GET.get('next'),
            # Top
            'topusers': topusers,
            'topnetworks': topnetworks,
            'topchallenges': topchallenges,
    })

    return render_to_response('welcome.html', context, context_instance=RequestContext(request))






# Take a forum id and redirect to the 'home' for that forum
# which will be on a network, course, module, or user profile
# This could probably be better handled with a template tag to generate the url preventing the redirects?
def forum_parent_redirect( request, forum_id ):
    forum = get_object_or_404( Forum, pk=forum_id )
    
    try:
        forum.network
    except:
        pass
    else:
        return redirect('network-detail', network_id=forum.network.id)

    try:
        forum.module
    except:
        pass
    else:
        return redirect('module-detail', module_id=forum.module.id)


def error500(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL
    })))

# Display topX by user, network and countries/etc.
# TODO: Move this out to a seperate statistics module in future
def statistics(request):

    from countries.models import Country

    topusers = User.objects.order_by('-userprofile__sq')[0:5]
    topnetworks = Network.objects.annotate( total_members=Count('usernetwork') ).order_by('-sq')[0:5]
    topcountries = Country.objects.annotate( total_members=Count('userprofile'), sq=Avg('userprofile__sq') ).order_by('-sq')[0:5]

    context = RequestContext(request, {
            'topusers': topusers,
            'topnetworks': topnetworks,
            'topcountries': topcountries,
    })

    return render_to_response('statistics.html', context, context_instance=RequestContext(request))



