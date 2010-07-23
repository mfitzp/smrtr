from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# Smrtr
from discuss.models import *
from discuss.forms import *
# from discuss.forms import *

# forum, newthread, thread, reply

def forum(request, forum_id):
    return False

def newthread(request, forum_id):

    forum = get_object_or_404(Forum, pk=forum_id)

    if request.method == 'POST':
        tform = ThreadForm(request.POST) 
        pform = PostForm(request.POST) 
        if tform.is_valid() and pform.is_valid():
            thread = tform.save(commit=False)
            post = pform.save(commit=False)
            
            thread.forum = forum
            thread.author = request.user
            thread.save()
            
            post.thread = thread
            post.author = request.user
            
            post.save() #FIXME: This will update the thread latest_post values and re-save it, wasteful
            
            return HttpResponseRedirect( reverse('discuss_forum',kwargs={'forum_id':forum.id} ) ) # Redirect to parent forum
    
    else:
        tform = ThreadForm()
        pform = PostForm()

    context = {
        'forum': forum,
        'tform': tform, 
        'pform': pform,
    }

    return render_to_response('newthread.html', context, context_instance=RequestContext(request))


def thread(request, thread_id):

    thread = get_object_or_404(Thread, pk=thread_id)
    
    context = {
        'forum': thread.forum,
        'thread': thread, 
        'title': thread,
    }

    return render_to_response('thread.html', context, context_instance=RequestContext(request))

def reply(request, thread_id):

    thread = get_object_or_404(Thread, pk=thread_id)
    forum = thread.forum

    if request.method == 'POST':
        form = PostForm(request.POST) 
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.thread = thread
            post.save()
            
            return HttpResponseRedirect( reverse('discuss_thread',kwargs={'thread_id':thread.id} ) ) # Redirect to parent forum
    
    else:
        form = PostForm()

    context = {
        'forum': forum,
        'thread': thread,
        'form': form,
    }

    return render_to_response('reply.html', context, context_instance=RequestContext(request))
    
