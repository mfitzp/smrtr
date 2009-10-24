from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.education.models import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_detail(request, network_id):

    network = get_object_or_404(Network, pk=network_id)
    memberships = network.memberships()

    # If the user is registered at this network, pull up their record for custom output (course listings, etc.)
    try:
        usernetwork = memberships.get( user=request.user )
    except:
        usernetwork = list()

    network.courses_filtered = list()

    # Find all courses being offered by this network
    for course in network.courses_offered.all():
        if course in request.user.courses.all():
            pass
        else:
            network.courses_filtered.append( course )

    # Find all courses owned by this network
    for course in network.course_set.all():
        if course in request.user.courses.all():
            pass
        else:
            network.courses_filtered.append( course )


    return render_to_response('education/network_detail.html', {'network': network, 'usernetwork': usernetwork, 'memberships': memberships})



# Get an insititution id and present a page showing detail
# if user is registered at the network, provide a tailored page
def network_register(request, network_id):

    network = get_object_or_404(Network, pk=network_id)

    if request.POST:
        un = UserNetwork()
        un.user = request.user
        
        try:
            un.network = network
            
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, un
            pass

        else:
            # Write to database 
            un.save()
            return HttpResponseRedirect(reverse('spenglr.core.views.index'))

    return render_to_response('education/network_register.html', {'network': network })





# Get an course id and present a page showing detail
# if user is registered on the course, provide a tailored page
def course_detail(request, network_id, course_id):

    network = get_object_or_404(Network, pk=network_id)
    course = get_object_or_404(Course, pk=course_id)

    memberships = course.memberships_context( network=network )

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usercourse = memberships.get( user=request.user )
    except:
        usercourse = list()

    course.modules_filtered = list()

    for module in course.modules.all():
        if module in request.user.modules.all():
            pass
        else:   
            course.modules_filtered.append( module )


    return render_to_response('education/course_detail.html', {'network': network, 'course': course, 'usercourse': usercourse, 'memberships': memberships})



# Get an insititution id and present a page showing detail
# if user is registered at the course, provide a tailored page
def course_register(request, network_id, course_id):

    network = get_object_or_404(Network, pk=network_id)
    course = get_object_or_404(Course, pk=course_id)

    if request.POST:
        uc = UserCourse()
        uc.user = request.user

        try:
            uc.network = network
            uc.course = course
            uc.start_date = request.POST['start_date']
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, un
            pass

        else:
            # Write to database 
            un.save()
            return HttpResponseRedirect(reverse('spenglr.core.views.index'))

    return render_to_response('education/course_register.html', {'network': network, 'course': course })



# Get an module id and present a page showing detail
# if user is registered on the module, provide a tailored page
def module_detail(request, network_id, course_id, module_id):

    network = get_object_or_404(Network, pk=network_id)
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)

    memberships = module.memberships_context( network, course )

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usermodule = memberships.get( user=request.user )
    except:
        usermodule = list()


    return render_to_response('education/module_detail.html', {'network': network, 'course': course, 'module': module, 'usermodule': usermodule, 'memberships': memberships})


# Get an insititution id and present a page showing detail
# if user is registered at the course, provide a tailored page
def module_register(request, network_id,  course_id, module_id):

    network = get_object_or_404(Network, pk=network_id)
    course = get_object_or_404(Course, pk=course_id)
    module = get_object_or_404(Module, pk=module_id)
    
    if request.POST:
        um = UserModule()
        um.user = request.user
        
        usercourse = course.memberships.get( user=request.user )
        um.usercourse = usercourse
        
        try:
            um.network = network
            um.course = course
            um.module = module
            um.start_date = request.POST['start_date']
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, un
            pass

        else:
            # Write to database 
            un.save()
            return HttpResponseRedirect(reverse('spenglr.core.views.index'))

    return render_to_response('education/module_register.html', {'network': network, 'course': course, 'module': module })


