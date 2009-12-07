from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
# Spenglr
from education.models import Module, UserCourse
from core.models import LoginForm


def index(request):
    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        usernetworks = request.user.usernetwork_set.all()
        usercourses = request.user.usercourse_set.all()

        i = RequestContext(request, {
            'usernetworks': usernetworks,
            'usercourses': usercourses,
        })
        
        return render_to_response('dashboard.html', i)
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        return HttpResponseRedirect("/accounts/login/")

