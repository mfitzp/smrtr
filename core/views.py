from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from spenglr.education.models import Module, UserCourse
from spenglr.core.models import LoginForm
from django.http import HttpResponseRedirect


def index(request):
    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        user_networks = request.user.usernetwork_set.all()
        user_courses = request.user.usercourse_set.all()
        i = RequestContext(request, {
            'user_networks': user_networks,
            'user_courses': user_courses,
        })
        return render_to_response('dashboard.html', i)
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        return HttpResponseRedirect("/accounts/login/")

