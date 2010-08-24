import datetime
# Django
from django.conf import settings
from django import http
from django.template import Context, RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.db.models import Q, F
from django.db.models import Avg, Max, Min, Count, Sum
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
# External
from wall.models import Wall, WallItem
from wall.forms import WallItemForm
# Smrtr
from network.models import Network
from challenge.models import Challenge, UserChallenge
from concept.models import Concept

from core.forms import LoginForm
from wallextend.models import add_extended_wallitem

def home(request):

    if request.user.is_authenticated():

        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        userchallenges = request.user.userchallenge_set.all()
        
        userchallengesactive = userchallenges.filter(percent_complete__lt=100) #.order_by('status') # Show all
        userchallengescomplete = userchallenges.filter(percent_complete__exact=100).order_by('-end_date')[0:3]

        # Flag True/False whether challenges exist at all for this user
        userchallengesexist = ( userchallengesactive.count() + userchallengescomplete.count() ) > 0
        
        # TODO: All the following need some mechanism to filter, reduce the number shown
        # Like +1, Comment +1 or +2
        # Personal rating/comment more weight than others (*2) e.g 
        
        # NOTE: Can  weight each network, challenge, concept by limiting
        # the max number of posts got from each at this point,
        # e.g. pull 5 from each concept, 10 from each network will *2 favour network posts
        
        # System announce wall
        wallitems = Wall.objects.get(pk=1).wallitem_set.select_related()
        
        # Posts on user's networks
        for un in usernetworks:
            if un.network.wall:
                wallitems = wallitems | un.network.wall.wallitem_set.select_related()
          
        # These need to be limited in some way?
        for uc in userchallenges:
            if uc.challenge.wall:
                wallitems = wallitems | uc.challenge.wall.wallitem_set.select_related()            

        # Default post wall = home network (if set)
        if request.user.get_profile().network:
            wall = request.user.get_profile().network.wall
        else:
            wall = None
                    
        i = RequestContext(request, {
            'usernetworks': usernetworks,

            # Challenges
            'userchallengesexist': userchallengesexist,
            'userchallengesactive': userchallengesactive,
            'userchallengescomplete': userchallengescomplete,
            
            # Combined wallitems available to this user, limited to 10 max
            'wallitems': wallitems[0:10],
            'wall': wall,
            'wall_is_home': True,
        })
        
        return render_to_response('dashboard.html', i, context_instance=RequestContext(request))
        
    else:
        # Not logged in
        return welcome(request)



def welcome(request):

    from django.contrib.auth.forms import AuthenticationForm

    topusers = User.objects.order_by('-userprofile__sq')[0:5]
    topnetworks = Network.objects.annotate( total_members=Count('usernetwork') ).order_by('-sq')[0:5]
    
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
            'wallitems': WallItem.objects.select_related()[0:5]
    })

    return render_to_response('welcome.html', context, context_instance=RequestContext(request))






# Take a wall id and redirect to the 'home' for that forum
# which will be on a network, course, challenge, or user profile
# This could probably be better handled with a template tag to generate the url preventing the redirects?
def wall_home_redirect( request, wall_slug ):
    wall = get_object_or_404( Wall, slug=wall_slug )

    try:
        wall.network
    except:
        pass
    else:
        return redirect( wall.network.get_absolute_url() )
        
    try:
        wall.challenge
    except:
        pass
    else:
        return redirect( wall.challenge.get_absolute_url() )
        
    try:
        wall.concept
    except:
        pass
    else:
        return redirect( wall.concept.get_absolute_url() )     
        
    try:
        wall.challenge
    except:
        pass
    else:
        return redirect( wall.challenge.get_absolute_url() )                

    # System announce wall (it has no home, sob)
    return redirect('home')

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
# TODO: Move this out to a seperate statistics challenge in future
def statistics(request):

    from countries.models import Country

    topusers_smart = User.objects.order_by('-userprofile__sq')[0:10]
    
    # Retrieve records for past month
    start_date = datetime.datetime.now() - datetime.timedelta(weeks=4)
    end_date = datetime.datetime.now()

    topusers_active = User.objects.filter(userquestionattempt__created__range=(start_date,end_date)).annotate(
                        activity_rating=Count('userquestionattempt')).order_by('-activity_rating')[0:10]

    

    topnetworks = Network.objects.annotate( total_members=Count('usernetwork') ).order_by('-sq')[0:10]
    topcountries = Country.objects.annotate( total_members=Count('userprofile'), sq=Avg('userprofile__sq') ).order_by('-sq')[0:10]

    context = RequestContext(request, {
            'topusers_smart': topusers_smart,
            'topusers_active': topusers_active,

            'topnetworks': topnetworks,
            'topcountries': topcountries,
    })

    return render_to_response('statistics.html', context, context_instance=RequestContext(request))



