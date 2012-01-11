from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils import simplejson as json
from django.views.decorators.cache import cache_control

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist
from pymongo.objectid import ObjectId

from depot.models import Resource, Curation, Location, CalendarEvent,  \
    STATUS_OK, STATUS_BAD
    # COLL_STATUS_NEW, COLL_STATUS_LOC_CONF, COLL_STATUS_TAGS_CONF, COLL_STATUS_COMPLETE #location_from_cb_value,
from depot.forms import FindResourceForm, ShortResourceForm, LocationUpdateForm, EventForm, \
    TagsForm, ShelflifeForm, CurationForm
    
# from firebox.views import get_terms
from engine_groups.models import Account, get_account

def get_one_or_404(obj_class=Resource, **kwargs):
    """helper function for Mongoengine documents"""
    try:
       user = kwargs.pop('user', None)
       perm = kwargs.pop('perm', None)
       object = obj_class.objects.get(**kwargs)
       if user and perm:
           if not user.has_perm(perm, object):
               raise PermissionDenied()
       return object
    except (MultipleObjectsReturned, ValidationError, DoesNotExist):
        raise Http404

def resource_index(request):

    objects = Resource.objects
    return render_to_response('depot/resource_list.html',
        RequestContext( request, { 'objects': objects }))

def resource_detail(request, object_id, template='depot/resource_detail.html'):

    object = get_one_or_404(id=ObjectId(object_id))

    return render_to_response(template,
        RequestContext( request, { 'object': object, 'yahoo_appid': settings.YAHOO_KEY, 'google_key': settings.GOOGLE_KEY }))

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
def resource_add(request, template='depot/resource_edit.html'):
    """adds a new resource"""
    
    template_info = _template_info(request.REQUEST.get('popup', ''))
    # formclass = ShortResourceForm
    

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return resource_edit_complete(request, None, template_info)
        form = ShortResourceForm(request.POST)
        if form.is_valid():
            resource = Resource(**form.cleaned_data)
            # resource.metadata.author = str(request.user.id)
            try:
                # resource.collection_status = COLL_STATUS_LOC_CONF
                user = get_account(request.user.id)
                resource.owner = user
                # save will create default moderation and curation using owner acct
                resource.save(author=user, reindex=True)
                # resource.index()
                # if popup:
                #     return HttpResponseRedirect(reverse('resource-popup-close'))
                return HttpResponseRedirect('%s?popup=%s' % (reverse('resource-edit', args=[resource.id]), template_info['popup']))
            except OperationError:
                pass
            
    else:
        description= request.GET.get('t', '').replace('||', '\n')
        initial = {
            'uri': request.GET.get('page', ''),
            'title': request.GET.get('title', ''),
            'description': description[:1250]
            }
        form = ShortResourceForm(initial=initial)
    
    return render_to_response(template,
        RequestContext( request, {'resourceform': form, 'template_info': template_info }))

@login_required
def resource_edit(request, object_id, template='depot/resource_edit.html'):
    """ edits an existing resource. Uses a wizard-like approach, so checks resource.collection_status
        and hands off to resource_* function handler
    """
    UPDATE_LOCS = 'Update locations'
    UPDATE_TAGS = 'Update tags'
    
    resource = get_one_or_404(id=ObjectId(object_id), user=request.user, perm='can_edit')

    # doc = ''
    # places = None
    template_info = _template_info(request.REQUEST.get('popup', ''))

    if request.method == 'POST':
        result = request.POST.get('result', '') # or request.POST.get('result', '')
        if result == 'Cancel':
            return resource_edit_complete(request, resource, template_info)
        resourceform = ShortResourceForm(request.POST, instance=resource)
        eventform = EventForm(request.POST, instance=resource.calendar_event)
        locationform = LocationUpdateForm(request.POST, instance=resource)
        # shelflifeform = ShelflifeForm(request.POST, instance=resource)
        
        if resourceform.is_valid() and locationform.is_valid() and eventform.is_valid():
            acct = get_account(request.user.id)

            # REPLACE FROM HERE
            new_loc = locationform.cleaned_data['new_location']
            if new_loc: 
                resource.add_location_from_name(locationform.cleaned_data['new_location'])
                resource.save(author=acct, reindex=True)
            else:
                event_start = eventform.cleaned_data['start']
                if event_start:
                    resource.calendar_event = CalendarEvent(start=event_start, end=eventform.cleaned_data['end'])
                    # print 'event_start', event_start
                    # print 'event_finish', eventform.cleaned_data['end']
                else:
                    resource.calendar_event = None
                resource = resourceform.save()
                
                try:
                    resource.save(author=acct, reindex=True)
                    return resource_edit_complete(request, resource, template_info)
                except OperationError:
                    pass

            # NEW SNEEU
            # # Location
            # new_loc = locationform.cleaned_data['new_location'].split(',')
            # print new_loc
            # resource.locations = Location.objects(id__in=new_loc)
            # #resource.add_location_from_name(locationform.cleaned_data['new_location'])
            # #resource.save(author=acct, reindex=True)

            # # Dates
            # event_start = eventform.cleaned_data['start']
            # if event_start:
            #     resource.calendar_event = CalendarEvent(start=event_start, end=eventform.cleaned_data['end'])
            #     # print 'event_start', event_start
            #     # print 'event_finish', eventform.cleaned_data['end']
            # else:
            #     resource.calendar_event = None
            # resource = resourceform.save()
            
            # try:
            #     resource.save(author=acct, reindex=True)
            #     return resource_edit_complete(request, resource, template_info)
            # except OperationError:
            #     pass



    else:
        resourceform = ShortResourceForm(instance=resource)
        locationform = LocationUpdateForm(instance=resource)
        eventform = EventForm(instance=resource.calendar_event)
        # if not resource.locations:
        #     doc = resource.uri
        # shelflifeform = ShelflifeForm(instance=resource)
    
    return render_to_response(template,
        RequestContext( request, { 'template_info': template_info, 'object': resource,
            'resourceform': resourceform, 'locationform': locationform, 'eventform': eventform, #'places': places,
            # 'tagsform': tagsform, #'shelflifeform': shelflifeform,
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

@login_required
def resource_remove(request, object_id):
    object = get_one_or_404(id=ObjectId(object_id), user=request.user, perm='can_delete')
    object.delete()
    return HttpResponseRedirect(reverse('resource-list'))

# @login_required
@cache_control(no_cache=False, public=True, must_revalidate=False, proxy_revalidate=False, max_age=300)
def resource_find(request, template='depot/resource_find.html'):
    """docstring for resource_find"""

    results = locations = []
    centre = None
    pins = []
    # places = []
    result = request.REQUEST.get('result', '')
    if request.method == 'POST' or result:
        # result = request.REQUEST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('resource-list'))
        form = FindResourceForm(request.REQUEST)
    
        if form.is_valid():
            user = get_account(request.user.id)
            for result in form.results:
                resource = get_one_or_404(id=ObjectId(result['res_id']))

                try:
                    curation_index, curation = get_curation_for_user_resource(user, resource)
                except TypeError:
                    curation_index = curation = None

                curation_form = CurationForm(
                        initial={'outcome': STATUS_OK},
                        instance=curation)
                results.append({
                    'resource_result': result,
                    'curation': curation,
                    'curation_form': curation_form,
                    'curation_index': curation_index
                })
                
            locations = form.locations
            centre = form.centre
            # pins = [loc['obj'] for loc in locations]
            
    else:
        form = FindResourceForm(initial={'post_code': 'aberdeen', 'boost_location': settings.SOLR_LOC_BOOST_DEFAULT})

    context = {
        'form': form,
        'results': results,
        'locations': locations,
        'centre': centre,
        'pins': pins,
        'yahoo_appid': settings.YAHOO_KEY,
        'google_key': settings.GOOGLE_KEY,
    }
    return render_to_response(template, RequestContext(request, context))


def curation_detail(request, object_id, index=None, template='depot/curation_detail.html'):
    """docstring for curation_detail"""
    if index:
        resource = get_one_or_404(id=ObjectId(object_id))
        curation = resource.curations[int(index)]
    else:
        curation = get_one_or_404(obj_class=Curation, id=ObjectId(object_id))        
        resource = curation.resource

    if request.is_ajax():
        context = {
            'curation': {
                'note': curation.note,
                'tags': curation.tags,
            },
            'resource': {
                'title': resource.title,
                'description': resource.description,
            },
            'url': reverse('curation-add', args=(resource.id, )),
        }
        return HttpResponse(json.dumps(context), mimetype='application/json')

    context = {
        'index': index,
        'object': curation,
        'resource': resource,
    }
    return render_to_response(template, RequestContext(request, context))


def curation_add(request, object_id, template_name='depot/curation_edit.html'):
    """docstring for curation_add"""
    resource = get_one_or_404(id=ObjectId(object_id))
    user = get_account(request.user.id)
    
    curation = get_curation_for_user_resource(user, resource)
    if curation:
        index, cur = curation
        messages.success(request, 'You already have a curation for this resource.')
        return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))

    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('resource', args=[resource.id]))
        form = CurationForm(request.POST)
        if form.is_valid():
            curation = Curation(**form.cleaned_data)
            curation.owner = user
            curation.item_metadata.update(author=user)
            curation.resource = resource
            curation.save()
            resource.curations.append(curation)
            resource.save(reindex=True)
            index = len(resource.curations) - 1
            
            return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))
    else:
        initial = { 'outcome': STATUS_OK}
        form = CurationForm(initial=initial)

    template_context = {'form': form}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )
    
# @user_passes_test(lambda u: u.is_staff)
@login_required
def curation_edit(request, object_id, index, template_name='depot/curation_edit.html'):
    """Curation is an EmbeddedDocument, so can't be saved, needs to be edited, then Resource saved."""

    resource = get_one_or_404(id=ObjectId(object_id), user=request.user, perm='can_edit')
    object = resource.curations[int(index)]
    
    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))
        form = CurationForm(request.POST, instance=object)
        if form.is_valid():
            user = get_account(request.user.id)
            curation = form.save(do_save=False)
            curation.item_metadata.update(author=user)
            curation.save()
            resource.save(reindex=True)
            return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))
    else:
        form = CurationForm(instance=object)

    template_context = {'form': form}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

    
@login_required
def curation_remove(request, object_id, index):
    """docstring for curation_remove"""
    resource = get_one_or_404(id=ObjectId(object_id), user=request.user, perm='can_delete')
    resource.curations[int(index)].delete()
    del resource.curations[int(index)]
    resource.save(reindex=True)
    return HttpResponseRedirect(reverse('resource', args=[resource.id]))
    
@login_required
def location_remove(request, object_id, index):
    """docstring for location_remove"""
    resource = get_one_or_404(id=object_id, user=request.user, perm='can_edit')
    del resource.locations[int(index)]
    resource.save(author=get_account(request.user.id), reindex=True)
    return HttpResponseRedirect(reverse('resource-edit', args=[resource.id]))
    
def curations_for_group(request, object_id, template_name='depot/curations_for_group.html'):
    """docstring for curations_for_group"""
    object = get_one_or_404(obj_class=Account, id=object_id)

    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]  
    template_context = {'object': object, 'curations': curations}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

def curations_for_group_html(request, object_id, template_name='depot/curations_for_group_embed.html'):

    object = get_one_or_404(obj_class=Account, id=ObjectId(object_id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    template_context = {'object': object, 'curations': curations}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )
    
def curations_for_group_js(request, object_id, template_name='depot/curations_for_group_embed.js'):
    
    object = get_one_or_404(obj_class=Account, id=ObjectId(object_id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    base_url = Site.objects.get_current().domain
    print base_url
    template_context = Context(
        {'object': object, 'curations': curations, 'base_url': 'http://%s' % base_url})

    response = HttpResponse(mimetype='text/javascript')
    t = loader.get_template(template_name)
    response.write(t.render(template_context))
    return response
    
def get_curation_for_user_resource(user, resource):
    # check if user already has a curation for this resource
    for index, cur in enumerate(resource.curations):
        if cur.owner.id == user.id:
            return index, cur
    return None
    
    
