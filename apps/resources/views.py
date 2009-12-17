from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
# Spenglr
from resources.models import Resource
from education.models import Module, ModuleInstance



def module_userresources(request, modulei_id):

    modulei = get_object_or_404(ModuleInstance, pk=modulei_id)
    module = modulei.module # Prefetch

    # If the user is registered on this module pull record
    try:
        usermodule = modulei.usermodule_set.get( user=request.user )
    except:
        usermodule = list()

    resources = Resource.objects.all().filter(question__modules=module, userresource__user=request.user).distinct()

    return render_to_response('module_userresources.html', {'module': module, 'modulei':modulei, 'usermodule':usermodule, 'resources': resources}, context_instance=RequestContext(request))
