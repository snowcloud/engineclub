from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist

from depot.models import Item, location_from_cb_value, \
    COLL_STATUS_NEW, COLL_STATUS_LOC_CONF, COLL_STATUS_TAGS_CONF, COLL_STATUS_COMPLETE
from depot.forms import *
from firebox.views import *

def get_one_or_404(**kwargs):
    try:
       object = Item.objects.get(**kwargs)
       return object
    except (MultipleObjectsReturned, ValidationError, DoesNotExist):
        raise Http404
    
    
def item_index(request):

    objects = Item.objects
    return render_to_response('depot/item_list.html',
        RequestContext( request, { 'objects': objects }))


def item_detail(request, object_id):

    object = get_one_or_404(id=object_id)

    return render_to_response('depot/item_detail.html',
        RequestContext( request, { 'object': object, 'yahoo_appid': settings.YAHOO_KEY }))
        

def _template_info(popup):
    """docstring for _template_info"""
    if popup:
        return {'popup': popup, 'base': 'base_popup.html'}
    else:
        return {'popup': popup, 'base': 'base.html'}
        
@login_required
def item_add(request):

    template_info = _template_info(request.REQUEST.get('popup', ''))
    # formclass = ShortItemForm
    template = 'depot/item_edit.html'

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return item_edit_complete(request, None, template_info)
        form = ShortItemForm(request.POST)
        if form.is_valid():
            item = Item(**form.cleaned_data)
            item.metadata.author = str(request.user.id)
            try:
                item.collection_status = COLL_STATUS_LOC_CONF
                item.save()
                # if popup:
                #     return HttpResponseRedirect(reverse('item-popup-close'))
                return HttpResponseRedirect('%s?popup=%s' % (reverse('item-edit', args=[item.id]), template_info['popup']))
            except OperationError:
                pass
            
    else:
        description= request.GET.get('t', '').replace('||', '\n')
        initial = {
            'url': request.GET.get('page', ''),
            'title': request.GET.get('title', ''),
            'description': description[:1250]
            }
        form = ShortItemForm(initial=initial)
    
    return render_to_response(template,
        RequestContext( request, {'form': form, 'template_info': template_info }))

@login_required
def item_remove(request, object_id):
    object = get_one_or_404(id=object_id)
    object.delete()
    return HttpResponseRedirect(reverse('item-list'))
    
@login_required
def item_edit(request, object_id):
    
    item = get_one_or_404(id=object_id)
    
    template_info = _template_info(request.REQUEST.get('popup', ''))

    fn = globals().get('item_%s' % item.collection_status, None)
    if fn:
        return fn(request, item, template_info)

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return item_edit_complete(request, item, template_info)
            
        form = ShortItemForm(request.POST, instance=item)
        form.instance = item
        if form.is_valid():
            item = form.save()
            item.author = str(request.user.id)
            try:
                item.collection_status = COLL_STATUS_LOC_CONF
                item.save()
                return HttpResponseRedirect('%s?popup=%s' % (reverse('item-edit', args=[item.id]), template_info['popup']))
            except OperationError:
                pass

    else:
        form = ShortItemForm(instance=item)
    
    return render_to_response('depot/item_edit.html',
        RequestContext( request, { 'template_info': template_info, 'form': form, 'object': item }))

@login_required
def item_location_confirm(request, item, template_info):

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return item_edit_complete(request, item, template_info)
        cb_places = request.POST.getlist('cb_places')
        locations = []
        for loc in cb_places:
            locations.append(location_from_cb_value(loc))
        if len(locations) > 0:
            item.locations = locations
        item.collection_status = COLL_STATUS_TAGS_CONF
        item.save()

        return HttpResponseRedirect('%s?popup=%s' % (reverse('item-edit', args=[item.id]), template_info['popup']))

    try:
        p = geomaker(item.url)
        places= p.places
    except:
        places = None
        # TODO add user message
        
    return render_to_response('depot/item_edit_location.html',
        RequestContext( request, { 'template_info': template_info, 'object': item, 'places': places }))

@login_required
def item_tags_confirm(request, item, template_info):

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return item_edit_complete(request, item, template_info)

        tags = request.POST.getlist('tags')

        item_edit_complete(request, item, template_info)
        
    else:
        tags = []
    # TODO get tags from Yahoo along with locations
    
    return render_to_response('depot/item_edit_tags.html',
        RequestContext( request, { 'template_info': template_info, 'object': item, 'tags': tags }))

@login_required
def item_edit_complete(request, item, template_info):
    if item:
        item.collection_status = COLL_STATUS_COMPLETE
        item.save()
        popup_url = reverse('item-popup-close')
        url = reverse('item', args=[item.id])
    else: # been cancelled
        popup_url = reverse('item-popup-cancel')
        url = reverse('item-list')
    
    if template_info['popup']:
        return HttpResponseRedirect(popup_url)
    else:
        return HttpResponseRedirect(url)


