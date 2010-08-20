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
from wall.models import Wall
from wall.forms import WallItemForm
# Smrtr
from network.models import Network
from education.models import Topic, UserTopic, Concept
from challenge.models import Challenge
from core.forms import LoginForm


def home(request):

    if request.user.is_authenticated():

        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        usertopics = request.user.usertopic_set.all()
        userchallenges = request.user.userchallenge_set.all()
        
        userchallengesactive = userchallenges.filter(status__lt=2).order_by('status') # Show all
        userchallengescomplete = userchallenges.filter(status__exact=2).order_by('-completed')[0:3]

        # If no userchallenges available, attempt to populate
        # FIXME: This is going to fire on every dashboard load until the user has some challenge
        # it's relatively quick/smart but still clunky. An 'event' trigger mechanism whereby
        # this is called when new topics are activated would be preferable (adding this directly
        # to the education app creates an unwanted dependency).
        if not userchallenges:
            if usertopics: # Only generate if there are topics available
                from challenge.utils import generate_userchallenges
                generate_userchallenges(request.user)
                userchallengesactive = request.user.userchallenge_set.filter(status__lt=2).order_by('status')
        
        # Flag True/False whether challenges exist at all for this user
        userchallengesexist = ( userchallengesactive.count() + userchallengescomplete.count() ) > 0
        
        # TODO: All the following need some mechanism to filter, reduce the number shown
        # Like +1, Comment +1 or +2
        # Personal rating/comment more weight than others (*2) e.g 
        
        # NOTE: Can  weight each network, topic, concept by limiting
        # the max number of posts got from each at this point,
        # e.g. pull 5 from each concept, 10 from each network will *2 favour network posts
        
        # System announce wall
        wallitems = Wall.objects.get(pk=1).wallitem_set.select_related()
        
        # Posts on user's networks
        for un in usernetworks:
            if un.network.wall:
                wallitems = wallitems | un.network.wall.wallitem_set.select_related()
          
        # These need to be limited to active only
        for ut in usertopics: 
            if ut.topic.wall:
                wallitems = wallitems | ut.topic.wall.wallitem_set.select_related()
            
        # These need to be limited to active only
        # filter: User has started/attempted the challenge
        # TODO: Challenge has not expired (once expiry added to challenges)
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
    })

    return render_to_response('welcome.html', context, context_instance=RequestContext(request))






# Take a wall id and redirect to the 'home' for that forum
# which will be on a network, course, topic, or user profile
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
        wall.topic
    except:
        pass
    else:
        return redirect( wall.topic.get_absolute_url() )
        
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
# TODO: Move this out to a seperate statistics topic in future
def statistics(request):

    from countries.models import Country

    topusers_smart = User.objects.order_by('-userprofile__sq')[0:10]
    
    # Retrieve records for past month
    start_date = datetime.now() - timedelta(weeks=4)
    end_date = datetime.now()

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



