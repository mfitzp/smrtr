from django.db import models
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from spenglr.education.models import Module, Course, UserModule, UserCourse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Get an course id and present a page showing detail
# if user is registered on the course, provide a tailored page
def course_detail(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usercourse = course.memberships.get( user=request.user )
    except:
        usercourse = list()

    course.modules_filtered = list()

    for module in course.modules.all():
        if module in request.user.modules.all():
            pass
        else:   
            course.modules_filtered.append( module )

    return render_to_response('education/course_detail.html', {'course': course, 'usercourse': usercourse})



# Get an insititution id and present a page showing detail
# if user is registered at the course, provide a tailored page
def course_register(request, course_id):

    course = get_object_or_404(Course, pk=course_id)

    if request.POST:
        un = UserCourse()
        un.user = request.user
        
        try:
            un.course = course
            un.start_date = request.POST['start_date']
        except:
            # Error when saving data, will need to redisplay form: error notifications here
            assert False, un
            pass

        else:
            # Write to database 
            un.save()
            return HttpResponseRedirect(reverse('spenglr.core.views.index'))

    return render_to_response('education/course_register.html', {'course': course })



# Get an module id and present a page showing detail
# if user is registered on the module, provide a tailored page
def module_detail(request, module_id):

    module = get_object_or_404(Module, pk=module_id)

    # If the user is registered at this institution, pull up their record for custom output (course listings, etc.)
    try:
        usermodule = module.memberships.get( user=request.user )
    except:
        usermodule = list()

    return render_to_response('education/module_detail.html', {'module': module, 'usermodule': usermodule})






