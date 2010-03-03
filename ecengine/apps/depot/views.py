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
# from placemaker.placemaker import Place

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

def update_item_metadata(self, item, request):
    """docstring for update_item_metadata"""
    item.metadata.author = str(request.user.id)
     
@login_required
def item_add(request):
    """adds a new item"""
    
    template_info = _template_info(request.REQUEST.get('popup', ''))
    # formclass = ShortItemForm
    template = 'depot/item_edit.html'

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return item_edit_complete(request, None, template_info)
        form = ShortItemForm(request.POST)
        if form.is_valid():
            item = Item(**form.cleaned_data)
            # item.metadata.author = str(request.user.id)
            try:
                # item.collection_status = COLL_STATUS_LOC_CONF
                item.save(str(request.user.id))
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
        RequestContext( request, {'itemform': form, 'template_info': template_info }))

@login_required
def item_remove(request, object_id):
    object = get_one_or_404(id=object_id)
    object.delete()
    return HttpResponseRedirect(reverse('item-list'))

def fix_places(item, doc=None):
    """docstring for fix_places"""
    result = []
    places = []
    itemlocs = {}
    for loc in item.locations:
        itemlocs[loc.woeid] = loc
        result.append(PlaceProxy(loc, checked=True))
    if doc:
        try:
            p = geomaker(doc)
            places= p.places
        except:
            places = []

    result.extend([place for place in places if unicode(place.woeid) not in itemlocs.keys()])  
    return result
    
@login_required
def item_edit(request, object_id):
    """ edits an existing item. Uses a wizard-like approach, so checks item.collection_status
        and hands off to item_* function handler
    """
    UPDATE_LOCS = 'Update locations'
    UPDATE_TAGS = 'Update tags'
    
    item = get_one_or_404(id=object_id)
    doc = ''
    places = None
    template_info = _template_info(request.REQUEST.get('popup', ''))

    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return item_edit_complete(request, item, template_info)
        itemform = ShortItemForm(request.POST, instance=item)
        locationform = LocationUpdateForm(request.POST, instance=item)
        tagsform = TagsForm(request.POST, instance=item)
        shelflifeform = ShelflifeForm(request.POST, instance=item)
        
        if itemform.is_valid() and locationform.is_valid() and tagsform.is_valid() and shelflifeform.is_valid():
            if result == UPDATE_LOCS:
                places = fix_places(item, locationform.content() or item.url)
            elif result == UPDATE_TAGS:
                places = fix_places(item, locationform.content() or item.url)
            else:
                item = itemform.save()
                
                # read location checkboxes
                cb_places = request.POST.getlist('cb_places')
                locations = []
                for loc in cb_places:
                    locations.append(location_from_cb_value(loc))
                # if len(locations) > 0:
                item.locations = locations

                item = tagsform.save()
                item = shelflifeform.save()
            
                try:
                    item.save(str(request.user.id))
                    return item_edit_complete(request, item, template_info)
                    # return HttpResponseRedirect('%s?popup=%s' % (reverse('item', args=[item.id]), template_info['popup']))
                except OperationError:
                    pass

    else:
        itemform = ShortItemForm(instance=item)
        locationform = LocationUpdateForm(instance=item)
        if not item.locations:
            doc = item.url
        places = fix_places(item, doc)
        tagsform = TagsForm(instance=item)
        shelflifeform = ShelflifeForm(instance=item)
    
    return render_to_response('depot/item_edit.html',
        RequestContext( request, { 'template_info': template_info, 'object': item,
            'itemform': itemform, 'locationform': locationform, 'places': places,
            'tagsform': tagsform, #'shelflifeform': shelflifeform,
            'UPDATE_LOCS': UPDATE_LOCS, 'UPDATE_TAGS': UPDATE_TAGS  }))

# @login_required
# def item_location_confirm(request, item, template_info):
# 
#     doc = ''
#     if request.method == 'POST':
#         form = LocationUpdateForm(request.POST)
#         result = request.POST.get('result', '')
#         if result == 'Cancel':
#             return item_edit_complete(request, item, template_info)
#         elif result.startswith('Update'):
#             if form.is_valid():
#                 doc = (form.content() or item.url)
#         else:
#             cb_places = request.POST.getlist('cb_places')
#             locations = []
#             for loc in cb_places:
#                 locations.append(location_from_cb_value(loc))
#             if len(locations) > 0:
#                 item.locations = locations
#             item.collection_status = COLL_STATUS_TAGS_CONF
#             item.save(str(request.user.id))
# 
#             return HttpResponseRedirect('%s?popup=%s' % (reverse('item-edit', args=[item.id]), template_info['popup']))
#     else:
#         form = LocationUpdateForm()
#         doc = item.url
#     try:
#         p = geomaker(doc)
#         places= p.places
#     except:
#         places = None
#         # TODO add user message
#         
#     return render_to_response('depot/item_edit_location.html',
#         RequestContext( request, { 'template_info': template_info, 'object': item,
#             'places': places, 'form': form }))
# 
# @login_required
# def item_tags_confirm(request, item, template_info):
# 
#     if request.method == 'POST':
#         if request.POST.get('result', '') == 'Cancel':
#             return item_edit_complete(request, item, template_info)
# 
#         tags = request.POST.getlist('tags')
# 
#         return item_edit_complete(request, item, template_info)
#         
#     else:
#         tags = []
#     # TODO get tags from Yahoo along with locations
#     
#     return render_to_response('depot/item_edit_tags.html',
#         RequestContext( request, { 'template_info': template_info, 'object': item, 'tags': tags }))
# 
@login_required
def item_edit_complete(request, item, template_info):
    if item:
        # item.collection_status = COLL_STATUS_COMPLETE
        item.save(str(request.user.id))
        popup_url = reverse('item-popup-close')
        url = reverse('item', args=[item.id])
    else: # item-add cancelled
        popup_url = reverse('item-popup-cancel')
        url = reverse('item-list')
    
    if template_info['popup']:
        return HttpResponseRedirect(popup_url)
    else:
        return HttpResponseRedirect(url)


