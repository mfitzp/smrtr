from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
# External
from wall.forms import WallItemForm

def profile(request, user_id):

    puser = get_object_or_404(User, pk=user_id)
    profile = puser.get_profile()

    try:
        wall = profile.wall
        wallitems = profile.wall.wallitem_set.select_related()
    except:
        wall = None
        wallitems = None

    context = {
        'puser': puser, 
        'profile': profile,
        "wall": wall,
        "wallitems": wallitems,
        "wallform": WallItemForm()
    }

    return render_to_response('profile.html', context, context_instance=RequestContext(request))