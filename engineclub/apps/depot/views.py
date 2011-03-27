from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist
from pymongo.objectid import ObjectId

from depot.models import Resource, Location,  \
    COLL_STATUS_NEW, COLL_STATUS_LOC_CONF, COLL_STATUS_TAGS_CONF, COLL_STATUS_COMPLETE #location_from_cb_value,
from depot.forms import *
from firebox.views import get_terms

def get_one_or_404(**kwargs):
    try:
       object = Resource.objects.get(**kwargs)
       return object
    except (MultipleObjectsReturned, ValidationError, DoesNotExist):
        raise Http404
    
def resource_index(request):

    objects = Resource.objects
    return render_to_response('depot/resource_list.html',
        RequestContext( request, { 'objects': objects }))

def resource_detail(request, object_id):

    object = get_one_or_404(id=ObjectId(object_id))

    return render_to_response('depot/resource_detail.html',
        RequestContext( request, { 'object': object, 'yahoo_appid': settings.YAHOO_KEY }))

def _template_info(popup):
    """docstring for _template_info"""
    if popup:
        return {'popup': popup, 'base': 'base_popup.html'}
    else:
        return {'popup': popup, 'base': 'base.html'}

def update_resource_metadata(self, resource, request):
    """docstring for update_resource_metadata"""
    resource.metadata.author = str(request.user.id)
     
@login_required
def resource_add(request):
    """adds a new resource"""
    
    template_info = _template_info(request.REQUEST.get('popup', ''))
    # formclass = ShortResourceForm
    template = 'depot/resource_edit.html'

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return resource_edit_complete(request, None, template_info)
        form = ShortResourceForm(request.POST)
        if form.is_valid():
            resource = Resource(**form.cleaned_data)
            # resource.metadata.author = str(request.user.id)
            try:
                # resource.collection_status = COLL_STATUS_LOC_CONF
                resource.save(str(request.user.id))
                # if popup:
                #     return HttpResponseRedirect(reverse('resource-popup-close'))
                return HttpResponseRedirect('%s?popup=%s' % (reverse('resource-edit', args=[resource.id]), template_info['popup']))
            except OperationError:
                pass
            
    else:
        description= request.GET.get('t', '').replace('||', '\n')
        initial = {
            'url': request.GET.get('page', ''),
            'title': request.GET.get('title', ''),
            'description': description[:1250]
            }
        form = ShortResourceForm(initial=initial)
    
    return render_to_response(template,
        RequestContext( request, {'resourceform': form, 'template_info': template_info }))

@login_required
def resource_remove(request, object_id):
    object = get_one_or_404(id=ObjectId(object_id))
    object.delete()
    return HttpResponseRedirect(reverse('resource-list'))

@login_required
def resource_edit(request, object_id):
    """ edits an existing resource. Uses a wizard-like approach, so checks resource.collection_status
        and hands off to resource_* function handler
    """
    UPDATE_LOCS = 'Update locations'
    UPDATE_TAGS = 'Update tags'
    
    resource = get_one_or_404(id=ObjectId(object_id))
    doc = ''
    places = None
    template_info = _template_info(request.REQUEST.get('popup', ''))

    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return resource_edit_complete(request, resource, template_info)
        resourceform = ShortResourceForm(request.POST, instance=resource)
        locationform = LocationUpdateForm(request.POST, instance=resource)
        tagsform = TagsForm(request.POST, instance=resource)
        shelflifeform = ShelflifeForm(request.POST, instance=resource)
        
        if resourceform.is_valid() and locationform.is_valid() and tagsform.is_valid() and shelflifeform.is_valid():
            if result == UPDATE_LOCS:
                pass
                # places = fix_places(resource.locations, locationform.content() or resource.url)
            elif result == UPDATE_TAGS:
                pass
                # places = fix_places(resource.locations, locationform.content() or resource.url)
            else:
                resource = resourceform.save()
                
                # read location checkboxes
                cb_places = request.POST.getlist('cb_places')
                locations = []
                for loc in cb_places:
                    locations.append(location_from_cb_value(loc).woeid)
                # if len(locations) > 0:
                resource.locations = locations

                resource = tagsform.save()
                resource = shelflifeform.save()
            
                try:
                    resource.save(str(request.user.id))
                    resource.reindex()
                    # try:
                    #     keys = get_terms(resource.url)
                    # except:
                    #     keys = [] # need to fail silently here
                    # resource.make_keys(keys)
                    return resource_edit_complete(request, resource, template_info)
                    # return HttpResponseRedirect('%s?popup=%s' % (reverse('resource', args=[resource.id]), template_info['popup']))
                except OperationError:
                    pass

    else:
        resourceform = ShortResourceForm(instance=resource)
        locationform = LocationUpdateForm(instance=resource)
        if not resource.locations:
            doc = resource.uri
        # places = fix_places(resource.locations, doc)
        tagsform = TagsForm(instance=resource)
        shelflifeform = ShelflifeForm(instance=resource)
    
    return render_to_response('depot/resource_edit.html',
        RequestContext( request, { 'template_info': template_info, 'object': resource,
            'resourceform': resourceform, 'locationform': locationform, 'places': places,
            'tagsform': tagsform, #'shelflifeform': shelflifeform,
            'UPDATE_LOCS': UPDATE_LOCS, 'UPDATE_TAGS': UPDATE_TAGS  }))

@login_required
def resource_edit_complete(request, resource, template_info):
    """docstring for resource_edit_complete"""
    
    if resource:
        # resource.collection_status = COLL_STATUS_COMPLETE
        resource.save(str(request.user.id))
        popup_url = reverse('resource-popup-close')
        url = reverse('resource', args=[resource.id])
    else: # resource-add cancelled
        popup_url = reverse('resource-popup-cancel')
        url = reverse('resource-list')
    
    if template_info['popup']:
        return HttpResponseRedirect(popup_url)
    else:
        return HttpResponseRedirect(url)

# @login_required
def resource_find(request):
    """docstring for resource_find"""

    results = locations = []
    centre = None
    pins = []
    # places = []
    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('resource-list'))
        form = FindResourceForm(request.POST)
    
        if form.is_valid():
            results = form.results
            locations = form.locations
            centre = form.centre
            # pins = [loc['obj'] for loc in locations]
            
    else:
        form = FindResourceForm(initial={ 'post_code': 'Ab10 1AX'})

    # print places
    return render_to_response('depot/resource_find.html',
        RequestContext( request, { 'form': form, 'results': results, 'locations': locations, 'centre': centre, 'pins': pins, 'yahoo_appid': settings.YAHOO_KEY }))
