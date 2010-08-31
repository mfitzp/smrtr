# Django
from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.template.loader import render_to_string
from django.utils import simplejson as json
# Smrtr
from package.models import *
from package.forms import *

from network.models import *
from questions.models import *
from resources.models import *
from core.http import Http403
# External
from haystack.query import SearchQuerySet
from countries.models import Country

# MODULE VIEWS

# Get an package id and present a page showing detail
# if user is registered on the package, provide a additional information
def detail(request, package_id):

    package = get_object_or_404(Package, pk=package_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    
    try:
        # userpackages "you are studying this package at..."
        userpackage = UserPackage.objects.get(package=package, user=request.user)
    except:
        userpackage = None

    # Generate filter list of challenges with associated user data
    package.challenges_filtered = list()
    
    if request.user.is_authenticated():
        for challenge in package.challenges.all().order_by('name'):
            if challenge in request.user.challenges.all():
                challenge.userchallenge = request.user.userchallenge_set.get( challenge = challenge )
            else:
                pass
            package.challenges_filtered.append(challenge)
    else:
        package.challenges_filtered = package.challenges.all().order_by('name')
          
    leaderboard = {
        'members'   : package.userpackage_set.exclude(percent_complete=0).order_by('-sq')[0:5],
        'networks'  : Network.objects.exclude(usernetwork__user__userpackage__percent_complete=0).filter(usernetwork__user__userpackage__package=package).annotate(leaderboard_previous_sq=Avg('usernetwork__user__userpackage__previous_sq'),leaderboard_sq=Avg('usernetwork__user__userpackage__sq'),leaderboard_percent_correct=Avg('usernetwork__user__userpackage__percent_correct'),total_members=Count('usernetwork__user__userpackage__percent_correct')).order_by('-leaderboard_sq')[0:5],
        'countries' : Country.objects.exclude(userprofile__user__userpackage__percent_complete=0).filter(userprofile__user__userpackage__package=package).annotate(leaderboard_previous_sq=Avg('userprofile__user__userpackage__previous_sq'),leaderboard_sq=Avg('userprofile__user__userpackage__sq'),leaderboard_percent_correct=Avg('userprofile__user__userpackage__percent_correct'),total_members=Count('userprofile__user__userpackage__percent_correct')).order_by('-leaderboard_sq')[0:5],
                    }          


    context = { 'package': package, 
                'userpackage': userpackage,
                'leaderboard': leaderboard,
                'total_members': package.users.count(),                
                # Wall items
                "wall": package.wall,
                "wallitems": package.wall.wallitem_set.all(),
                'next':request.GET.get('next')
              }

    return render_to_response('package_detail.html', context, context_instance=RequestContext(request) )


@login_required
def register(request, package_id):

    package = get_object_or_404(Package, pk=package_id)

    if request.method == 'POST':
        uc = UserPackage()
        uc.user = request.user
        uc.package = package
        uc.save()

        request.user.message_set.create(
        message=_(u"You are now studying ") + package.name)

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('package-detail', package_id=package.id)

    return redirect('package-detail', package_id=package.id)

# Remove a user from the specified package
@login_required
def unregister(request, package_id):

    package = get_object_or_404(Package, pk=package_id)
    userpackage = get_object_or_404(UserPackage, package=package, user=request.user)

    if request.method == 'POST':
        userpackage.delete()

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return redirect('package-detail', package_id=package.id)

    return redirect('package-detail', package_id=package.id)



# Get an package id and present a page showing detail
# if user is registered on the package, provide a additional information
def providers(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    providers = package.networks.all()
    return render_to_response('package_providers.html', {'package': package, 'providers': providers}, context_instance=RequestContext(request))




# Create a new package
@login_required
def create(request):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403
                
    if request.POST:
        form = PackageForm(request, request.POST)       

        if form.is_valid(): # All validation rules pass
            package = form.save()
            package.save()
            
            # Add ourselves to the package
            UserPackage(user=request.user,package=package).save()
            
            return redirect(package.get_absolute_url()) # Redirect to default view for the package
    else:
        form = PackageForm(request)
   
    context = { 
        'form': form,
        'package': None,
    }
    
    return render_to_response("package_edit.html", context, context_instance=RequestContext(request)) 
    
    

# Edit a package
@login_required
def edit(request, package_id):

    if not (request.user.is_staff or request.user.is_superuser):
        raise Http403

    package = get_object_or_404(Package, pk=package_id)
                    
    if request.POST:
        form = PackageForm(request, request.POST, instance=package)       

        if form.is_valid(): # All validation rules pass
            package = form.save()
            return redirect(package.get_absolute_url()) # Redirect to default view for the challenge
    else:
        form = PackageForm(request, instance=package) # Allow prepopulate  
   
    context = { 
        'form': form,
        'package': package,
    }
    
    return render_to_response("package_edit.html", context, context_instance=RequestContext(request))   
  
   
    
# Presents a search mechanism to find packages to activate (optionally) (free text and tags)
@login_required
def search( request, 
                    template_name='package_search.html',
                    next=None ):
    
    from package.forms import PackageSearchForm
    
    if request.POST.get('addpackage'):
        
        mids = request.POST.getlist('addpackage')
        
        for mid in mids:
            package = Package.objects.get(pk=mid)
            userpackage = UserPackage( user=request.user, package=package  )
            try:
                userpackage.save()
            except:
                messages.warning(request, _(u"You have already activated %s" % package.name ) )
            else:
                messages.success(request, _(u"You have activated %s" % package.name ) )
        if next:
            return redirect( next )

    query = ''
    results = []
    # RelatedSearchQuerySet().filter(content='foo').load_all()

    sqs = SearchQuerySet().models(Package)
    
    #from network.utils import searchqueryset_usernetwork_boost
    #sqs = searchqueryset_usernetwork_boost( request, sqs )    
    
    
    

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q':' '} #Default search return all
        
    form = PackageSearchForm(querydata, searchqueryset=sqs, load_all=True )

    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search()
        
    paginator = Paginator(list(results), 10)
        
    try:
        page_obj = paginator.page(int(request.GET.get('page', 1)))
    except (ValueError, EmptyPage, InvalidPage): 
        raise Http404("No such page of results!")    
        
    
    context = { 
        'form': form,
        'query': query,
        'results': results,
        'next' : next,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))    
















@login_required
def newset(request, package_id):

    if request.POST:
        package = get_object_or_404(Package, pk=package_id)
        userpackage = get_object_or_404(UserPackage, package=package, user=request.user)

        userpackage.generate_packageset(exclude_current_packageset=True)
        userpackage.save()
            
        next = request.GET.get('next')

        if next:
            return redirect(next)
        else:
            return redirect('home')
        
@login_required
def newset_ajax(request, package_id):

    package = get_object_or_404(Package, pk=package_id)
    userpackage = get_object_or_404(UserPackage, package=package, user=request.user)
    userpackage.generate_packageset(exclude_current_packageset=True)
    userpackage.save()

    result = { 
        'id':package_id,
        'content':render_to_string('_packageset_meta.html', { 'packageset':userpackage.packageset, 'userpackage':userpackage } ) 
        }       

    response = HttpResponse()
    json.dump(result, response)
    
    return response





# Add challenges to the package
# TODO: Provide mechanism for deletion
#@login_required
def add_challenges(request, package_id):
    from challenge.forms import ChallengeSearchForm
    
    package = get_object_or_404(Package, pk=package_id)
    
    # Get usernetwork of the challenge's 'home network'
    # must be a member of the network to add questions
    # additional limitations may be set by the network

    if request.POST.get('addchallenge'):
        
        cids = request.POST.getlist('addchallenge')
        
        for cid in cids:
            package.challenges.add( Challenge.objects.get( pk=cid ) )
            
        # Update total_question count for this challenge
        # used to highlight empty challenges and to exclude them from packages
        # package.total_questions = package.challenges.count()
        package.save()
        
        messages.success( request, _(u"%s challenges added to %s" % ( len(cids) , package.name ) ) )
        
        #if request.POST.get('next'):
            

    if request.GET.get('q'):
        querydata = request.GET
    else:
        querydata = {'q': package.name}

    sqs = SearchQuerySet().models(Challenge)

    form = ChallengeSearchForm(querydata, searchqueryset=sqs, load_all=True )
    results = []
    
    if form.is_valid():
        query = form.cleaned_data['q']
        results = form.search()

    paginator = Paginator(list(results), 10)
        
    try:
        page_obj = paginator.page(int(request.GET.get('page', 1)))
    except (ValueError, EmptyPage, InvalidPage): 
        raise Http404("No such page of results!")    

    context = { 
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'package': package, 
    }

    return render_to_response('package_add_challenges.html', context, context_instance=RequestContext(request))    




