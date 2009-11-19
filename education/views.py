from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.education.models import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


# Get an course id and present a page showing detail
# if user is registered on the course, provide a additional information
def course_detail(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    # usercourses "you are studying this course at..."
    usercourses = UserCourse.objects.filter(coursei__course=course)

    return render_to_response('education/course_detail.html', {'course': course, 'usercourses': usercourses})


# Get a course instance object and present as a page showing the detail
# if user is registered on the course, provide additional information
def coursei_detail(request, coursei_id):

    coursei = get_object_or_404(CourseInstance, pk=coursei_id)
    course = coursei.course # Shortcut

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usercourse = coursei.usercourse_set.get( user=request.user )
    except:
        usercourse = list()
    else:
        # Generate filter list of modules with associated user data
        # If user registered attach usermodule linker and prepend (top list)
        # else append (bottom list)
        course.modulei_filtered = list()
    
        for modulei in course.moduleinstance_set.all():
            if modulei in request.user.modules.all():
                pass
            else:
                course.modulei_filtered.append(modulei)
                    

    return render_to_response('education/coursei_detail.html', {'course': course, 'coursei': coursei, 'usercourse': usercourse})


# Get an insititution id and present a page showing detail
# if user is registered at the course, provide a tailored page
def coursei_register(request, coursei_id):

    network = get_object_or_404(Network, pk=network_id)
    coursei = get_object_or_404(CourseInstance, pk=course_id)

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

    return render_to_response('education/coursei_register.html', {'network': network, 'course': course })


# Get an course id and present a page showing detail
# if user is registered on the course, provide a additional information
def course_detail_providers(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    # usercourses "you are studying this course at..."
    usercourses = UserCourse.objects.filter(coursei__course=course)

    return render_to_response('education/course_detail.html', {'course': course, 'usercourses': usercourses})



# Get an module id and present a page showing detail
# if user is registered on the module, provide a tailored page
def module_detail(request, module_id):

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

# Get an module instance id and present a page showing detail
# if user is registered on the module, provide a tailored page
def modulei_detail(request, modulei_id):

    # ModuleInstance gives us course/module information
    modulei = get_object_or_404(ModuleInstance, pk=modulei_id)
    module = modulei.module # Shortcut

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usermodule = modulei.usermodule_set.get( user=request.user )
    except:
        usermodule = list()

    return render_to_response('education/modulei_detail.html', {'modulei': modulei, 'module': module, 'usermodule': usermodule})



# Get an insititution id and present a page showing detail
# if user is registered at the course, provide a tailored page
def modulei_register(request, modulei_id):

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

    return render_to_response('education/modulei_register.html', {'network': network, 'course': course, 'module': module })


