from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from spenglr.study.models import UserCourse
from spenglr.core.models import LoginForm
from django.http import HttpResponseRedirect


def index(request):
    if request.user.is_authenticated():
        # User logged in, present the user dashboard
        user_curriculum = UserCourse.objects.filter(user=request.user)
        c = RequestContext(request, {
            'user_curriculum': user_curriculum,
        })
        return render_to_response('dashboard.html', c)
    else:
        # User not logged in, provide login/signup form (no anonymous users)
        form = LoginForm()
        return render_to_response('welcome.html', {
                'form' : form,
        })

        

def loginhandler(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    return HttpResponseRedirect("/")
                else:
                    # Return a 'disabled account' error message
                    error = u'account disabled'
                    return errorHandle(error)
            else:
                 # Return an 'invalid login' error message.
                error = u'invalid login'
                return errorHandle(error)
        else:
            error = u'form is invalid'
            return errorHandle(error)
    else:
        form = LoginForm() # An unbound form
        return render_to_response('welcome.html', {
            'form': form,
        })