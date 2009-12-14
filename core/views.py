from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.http import HttpResponsePermanentRedirect
from django.db.models import Q
# Spenglr
from education.models import Module, UserCourse
from core.models import LoginForm
# External
from notification.models import Notice
from wall.views import *


def index(request):
    # External
    from wall.forms import WallItemForm

    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        usercourses = request.user.usercourse_set.all()

        notices = Notice.objects.notices_for(request.user, on_site=True)

        # Front page wallitems (wi) combine the user's accessible wall posts from 
        # user profile, networks, courses and modules (& friends later)
        
        # Posts to user's personal wall (profile)
        wi = request.user.get_profile().wall.wallitem_set.select_related()
        # Posts on user's networks, courses, modules
        for un in usernetworks:
            wi = wi | un.network.wall.wallitem_set.select_related()
        for uc in usercourses:
            wi = wi | uc.coursei.course.wall.wallitem_set.select_related()        
            for um in uc.usermodule_set.all():
                wi = wi | um.modulei.module.wall.wallitem_set.select_related()        

        # Filter out to show only *other* users - may not want this as comments/etc. on user's 
        # own posts will be missed? Depends on the profile/dashboard interaction - future
        # No __ne filter here?! Use combination of lt, gt for result
        # wi = wi.filter(Q(author__id__lt=request.user.id) | Q(author__id__gt=request.user.id))

        # TODO: Resulting queryset must be filtered to only show those users actually on
        # the user's own networks (option configuration switching here)
        # wi = wi.filter(author=request.user)
        wi = wi.filter(author__usernetwork__network__usernetwork__user=request.user).distinct()

        i = RequestContext(request, {
            'usernetworks': usernetworks,
            'usercourses': usercourses,
            # Wall objects
            # -wall should remain user's own wall on dashboard view (post>broadcast on user's page)
            # -wallitems should be combination of all user's available walls
            'wall': request.user.get_profile().wall,
            'wallitems': wi,
            'wallform': WallItemForm()
        })
        
        return render_to_response('dashboard.html', i, context_instance=RequestContext(request))
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        return HttpResponseRedirect("/accounts/login/")

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
        wall.course
        # Need to implement coursei cover here
        return HttpResponseRedirect(reverse('course-detail', kwargs={'course_id':wall.course.id}))
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

