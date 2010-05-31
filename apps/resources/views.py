from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
# Spenglr
from resources.models import Resource
from education.models import Concept
# External
from tagging.models import Tag,TaggedItem

def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    ary = ['http://video.flowplayer.org/fake_empire.mp3','http://blip.tv/file/get/KimAronson-TwentySeconds58192.flv']
    return render_to_response('resource_detail.html', {'resource': resource, 'ary':ary}, context_instance=RequestContext(request))

def resources_tagged(request,tag_id):
    tag = Tag.objects.get(pk=tag_id)
    resources = TaggedItem.objects.get_by_model(Resource, tag)

    return render_to_response('resource_tag_list.html', {'tag': tag, 'resources': resources}, context_instance=RequestContext(request))


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
     
