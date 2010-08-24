from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
# Spenglr
from resources.models import Resource
# External
from tagging.models import Tag,TaggedItem

def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    return render_to_response('resource_detail.html', {'resource': resource}, context_instance=RequestContext(request))

def resources_tagged(request,tag_id):
    tag = Tag.objects.get(pk=tag_id)
    resources = TaggedItem.objects.get_by_model(Resource, tag)

    return render_to_response('resource_tag_list.html', {'tag': tag, 'resources': resources}, context_instance=RequestContext(request))

