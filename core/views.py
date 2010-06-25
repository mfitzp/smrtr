from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.http import HttpResponsePermanentRedirect
from django.db.models import Q
from django.contrib.auth.models import User
# Spenglr
from education.models import Module, UserModule, Concept
from core.forms import LoginForm
# External
from notification.models import Notice
from wall.views import *

def index(request):
    # External
    from wall.forms import WallItemForm

    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        usermodules = request.user.usermodule_set.all()
        userconcepts = request.user.userconcept_set.filter(focus__gt=0).order_by('-focus')

        userchallenges = request.user.userchallenge_set.filter(status__lt=2).order_by('status')[0:5]
        userchallengescomplete = request.user.userchallenge_set.filter(status__exact=2)[0:3]
        # If no userchallenges available, attempt to populate
        # FIXME: This is going to fire on every dashboard load until the user has some challenge
        # it's relatively quick/smart but still clunky. An 'event' trigger mechanism whereby
        # this is called when new modules are activated would be preferable (adding this directly
        # to the education app creates an unwanted dependency).
        if not userchallenges:
            from challenge.utils import generate_user_challenges
            generate_user_challenges(request.user)
        
        # Flag True/False whether challenges exist at all for this user
        userchallengesexist = ( userchallenges.count() + userchallengescomplete.count() ) > 0
        
        # Get next activated concepts (available by modules reverse SQ), retrieving 5
        # Gets all concepts that are available (on user's modules) but not active
        # Later limit by 'dependencies on individual entries'
        # suggestconcepts = Concept.objects.exclude(userconcept__user=request.user).filter(module__usermodule__user=request.user).order_by('-sq')[0:3]
        suggestmodules = Module.objects.exclude(usermodule__user=request.user).filter(network__usernetwork__user=request.user).order_by('-sq')[0:3]

        notices = Notice.objects.notices_for(request.user, on_site=True)

        # Top users for front page (will want network top users later also, perhaps)
        topusers = User.objects.order_by('-userprofile__sq')[0:5]

        # Front page wallitems (wi) combine the user's accessible wall posts from 
        # user profile, networks, courses and modules (& friends later)
        
        # Posts to user's personal wall (profile) *ALWAYS* appear
        wi = request.user.get_profile().wall.wallitem_set.select_related()
        
        # TODO: All the following need some mechanism to filter, reduce the number shown
        # Like +1, Comment +1 or +2
        # Personal rating/comment more weight than others (*2) e.g 
        
        # NOTE: Can  weight each network, module, concept by limiting
        # the max number of posts got from each at this point,
        # e.g. pull 5 from each concept, 10 from each network will *2 favour network posts
        
        # Posts on user's networks, courses, modules
        for un in usernetworks:
            wi = wi | un.network.wall.wallitem_set.select_related()
            
        # These need to be limited to active only
        for um in usermodules:
            wi = wi | um.module.wall.wallitem_set.select_related()        
                      
        for uc in userconcepts:
            wi = wi | uc.concept.wall.wallitem_set.select_related()        
                    
                    
        # Filter out to show only *other* users - may not want this as comments/etc. on user's 
        # own posts will be missed? Depends on the profile/dashboard interaction - future
        # No __ne filter here?! Use combination of lt, gt for result
        # wi = wi.filter(Q(author__id__lt=request.user.id) | Q(author__id__gt=request.user.id))

        # TODO: Resulting queryset must be filtered to only show those users actually on
        # the user's own networks (option configuration switching here)
        # wi = wi.filter(author=request.user)
        #wi = wi.filter(author__usernetwork__network__usernetwork__user=request.user).distinct()
    
        from settings import SMRTR_FREE_TIME_URL

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
            
            'SMRTR_FREE_TIME_URL': SMRTR_FREE_TIME_URL,

            # Extras
            'topusers': topusers,
            
            # Wall objects
            # -wall should remain user's own wall on dashboard view (post>broadcast on user's page)
            # -wallitems should be combination of all user's available walls
            # 'wall': request.user.get_profile().wall,
            'wallitems': wi[0:10],
            #'wallform': WallItemForm()
        })
        
        return render_to_response('dashboard.html', i, context_instance=RequestContext(request))
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        return HttpResponseRedirect("/accounts/login/")


def welcome(request):
    from django.contrib.auth.forms import AuthenticationForm
    from education.models import Module
    from network.models import Network
    from django.db.models import Count

    topusers = User.objects.order_by('-userprofile__sq')[0:5]
    topnetworks = Network.objects.annotate(num_users=Count('usernetwork')).order_by('num_users')[0:10]
    topmodules = Module.objects.annotate(num_users=Count('usermodule')).order_by('num_users')[0:10]
    
    authentication_form = AuthenticationForm
    
    context = {
            'form' : authentication_form(request),
            # Top
            'topusers': topusers,
            'topnetworks': topmodules,
            'topmodules': topmodules,

    }

    return render_to_response('welcome.html', context, context_instance=RequestContext(request))






# Take a wall slug and redirect to the spenglr 'home' for that wall
# which will be on a network, course, module, or user profile
# This could probably be better handled with a template tag to generate the url preventing the redirects?
def wall_home( request, slug ):
    wall = get_object_or_404( Wall, slug=slug )
    
    try:
        wall.network
        return HttpResponseRedirect(reverse('network-detail', kwargs={'network_id':wall.network.id}))
    except:
        pass

    try:
        wall.module
        #Need to implement coursei cover here
        return HttpResponseRedirect(reverse('module-detail', kwargs={'module_id':wall.module.id}))
    except:
        pass

    try:
        wall.userprofile
        return HttpResponseRedirect(reverse('user-profile', kwargs={'user_id':wall.userprofile.user.id}))
    except:
        return HttpResponseRedirect(reverse('home'))


def wall_add( request, slug ):
    if request.POST:
        success_url = request.POST['success_url']
    else:
        success_url = False
    return add( request, slug, success_url=success_url)
        

def wall_edit( request, id ):

    if request.POST:
        success_url = request.POST['success_url']
    else:
        success_url = False
    return edit( request, id, success_url=success_url)



