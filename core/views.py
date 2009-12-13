from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
# Spenglr
from education.models import Module, UserCourse
from core.models import LoginForm
# External
from notification.models import Notice


def index(request):
    # External
    from wall.forms import WallItemForm

    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        usercourses = request.user.usercourse_set.all()

        notices = Notice.objects.notices_for(request.user, on_site=True)

        i = RequestContext(request, {
            'usernetworks': usernetworks,
            'usercourses': usercourses,
            # Wall objects
            # -wall should remain user's own wall on dashboard view (post>broadcast on user's page)
            # -wallitems should be combination of all user's available walls
            'wall': request.user.get_profile().wall,
            'wallitems': request.user.get_profile().wall.wallitem_set.select_related(),
            'wallform': WallItemForm()
        })
        
        return render_to_response('dashboard.html', i, context_instance=RequestContext(request))
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        return HttpResponseRedirect("/accounts/login/")

