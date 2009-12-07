from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User

def profile(request, user_id):
    
    user = get_object_or_404(User, pk=user_id)
    profile = user.get_profile()

    return render_to_response('profile.html', {'user': user, 'profile': profile}, context_instance=RequestContext(request))