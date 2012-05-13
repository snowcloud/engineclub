from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils import simplejson as json
from django.utils.http import urlquote_plus
from django.views.decorators.cache import cache_control

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist
from bson.objectid import ObjectId

from analytics.shortcuts import (increment_queries, increment_locations,
    increment_resources, increment_resource_crud)
from locations.models import Location, lookup_postcode
from resources.models import Resource, Curation, add_curation, CalendarEvent,  \
    STATUS_OK, STATUS_BAD, Moderation
    # COLL_STATUS_NEW, COLL_STATUS_LOC_CONF, COLL_STATUS_TAGS_CONF, COLL_STATUS_COMPLETE #location_from_cb_value,
from resources.forms import FindResourceForm, ShortResourceForm, LocationUpdateForm, EventForm, \
    TagsForm, ShelflifeForm, CurationForm, ResourceReportForm
from ecutils.utils import get_one_or_404, get_pages
from issues.models import (Issue, SEVERITY_LOW, SEVERITY_MEDIUM,
    SEVERITY_HIGH, SEVERITY_CRITICAL)

from accounts.models import Account, get_account


def resource_index(request):

    objects = get_pages(request, Resource.objects.order_by('title'), 30)

    return render_to_response('depot/resource_list.html',
        RequestContext( request, { 'objects': objects }))

def resource_detail(request, object_id, template_name='depot/resource_detail.html'):
    object = get_one_or_404(Resource, id=ObjectId(object_id))
    increment_resources(object_id)

    return render_to_response(template_name,
        RequestContext( request, { 'object': object, 'yahoo_appid': settings.YAHOO_KEY, 'google_key': settings.GOOGLE_KEY }))

@login_required
def resource_report(request, object_id, template_name='depot/resource_report.html'):
    """
    View for reporting a report when a user finds a problem with it.
    """
    resource = get_one_or_404(Resource, id=ObjectId(object_id))
    reporter=get_account(request.user.id)

    # if 'next' in request.GET:
    #     url = request.GET['next']
    # else:
    #     url = None
    # url = url or reverse('resource', args=[resource.id])

    if Issue.objects(reporter=reporter, related_document=resource).count():
        messages.warning(request, 'You have already reported this resource.')
        return HttpResponseRedirect(reverse('resource', args=[resource.id]))

    if request.method == 'POST':
        form = ResourceReportForm(request.POST)
        if form.is_valid():

            severity=int(form.cleaned_data['severity'])
            message=form.cleaned_data['message']

            issue = Issue(
                message=message,
                severity=severity,
                reporter=reporter)
            issue.related_document = resource
            issue.save()
            issue.notify_created()
            
            # only moderate as STATUS_BAD if SEVERITY_CRITICAL
            if severity == SEVERITY_CRITICAL:
                resource.moderate_as_bad(reporter)

            return HttpResponseRedirect(reverse('issue_detail', args=[issue.id]))
    else:
        form = ResourceReportForm()

    return render_to_response(template_name, {
        'next': urlquote_plus(request.GET.get('next', '')),
        'form': form,
        'object': resource,
    }, RequestContext(request))

def _template_info(popup):
    """docstring for _template_info"""
    if popup:
        return {'popup': popup, 'base': 'base_popup.html'}
    else:
        return {'popup': popup, 'base': 'depot/resource_base.html'}

def update_resource_metadata(self, resource, request):
    """docstring for update_resource_metadata"""
    resource.metadata.author = str(request.user.id)

def get_req_data(req_path):
    """
    given url like:
    /depot/resource/add/popup|true/title|Inverclyde%20Globetrotters%20%7C%20Facebook/page|http%3A%2F%2Fwww.facebook.com%2FInverclydeGlobetrotters/t|Having%20fun%20staying%20active%20by%20virtually%20walking%20around%20the%20world%20(and%20beyond!)%20without%20leaving%20Greenock
    
    gets an input path like:
    u'/depot/resource/add/popup|true/title|Inverclyde Globetrotters | Facebook/page|http~~www.facebook.com/InverclydeGlobetrotters/t|Having fun staying active by virtually walking around the world (and beyond!) without leaving Greenock'
    
    and returns a dict like:
    {u't': u'Having fun staying active by virtually walking around the world (and beyond!) without leaving Greenock', u'popup': u'true', u'page': u'http~~www.facebook.com/InverclydeGlobetrotters', u'title': u'Inverclyde Globetrotters | Facebook'})
    """
    result = {}

    POPUP = u'popup'
    LEN_POPUP = 7
    TITLE = u'title'
    LEN_TITLE = 7
    PAGE = u'page'
    LEN_PAGE = 6
    TEXT = u't'
    LEN_TEXT = 3

    i_popup = req_path.find(u'/%s|' % POPUP)
    i_title = req_path.find(u'/%s|' % TITLE)
    i_page = req_path.find(u'/%s|' % PAGE)
    i_text = req_path.find(u'/%s|' % TEXT)

    print i_popup, i_title, i_page, i_text

    if i_popup == -1 or i_title == -1 or i_page == -1 or i_text == -1:
        for i in req_path.split('/'):
            item = i.split('|')
            if len(item) > 1:
                result[item[0]] = item[1]
        return result
    else:
        result[POPUP] = req_path[i_popup+LEN_POPUP:i_title]
        result[TITLE] = req_path[i_title+LEN_TITLE:i_page]
        result[PAGE] = req_path[i_page+LEN_PAGE:i_text]
        result[TEXT] = req_path[i_text+LEN_TEXT:]

    return result

@login_required
def resource_add(request, template_name='depot/resource_edit.html'):
    """adds a new resource"""

    import urllib

    # seems url becomes http:/ on server- no idea why
    # defensive coding ftw.
    req_path = urllib.unquote(request.path).replace('http://', 'http~~').replace('http:/', 'http~~').replace('||', '\n')
    req_data = get_req_data(req_path)
    debug_info = (req_path, req_data)

    template_info = _template_info(req_data.get('popup', ''))

    if request.method == 'POST':
        if request.POST.get('result', '') == 'Cancel':
            return resource_edit_complete(request, None, template_info)
        form = ShortResourceForm(request.POST)
        if form.is_valid(request.user):
            resource = Resource(**form.cleaned_data)
            # resource.metadata.author = str(request.user.id)
            try:
                # resource.collection_status = COLL_STATUS_LOC_CONF
                user = get_account(request.user.id)
                resource.owner = user
                # save will create default moderation and curation using owner acct
                resource.save(author=user, reindex=True)
                increment_resource_crud('resouce_add', account=user)
                # resource.index()
                # if popup:
                #     return HttpResponseRedirect(reverse('resource-popup-close'))
                return HttpResponseRedirect('%s?popup=%s' % (reverse('resource_edit', args=[resource.id]), template_info['popup']))
            except OperationError:
                pass

    else:
        description= req_data.get('t', '')
        initial = {
            'uri': req_data.get('page', '').replace('http~~', 'http://'),
            'title': req_data.get('title', ''),
            'description': description[:1250]
            }
        form = ShortResourceForm(initial=initial)

    return render_to_response(template_name,
        RequestContext( request, {'resourceform': form, 'template_info': template_info, 'debug_info': debug_info }))

@login_required
def resource_edit(request, object_id, template_name='depot/resource_edit.html'):
    """ edits an existing resource. Uses a wizard-like approach, so checks resource.collection_status
        and hands off to resource_* function handler
    """
    UPDATE_LOCS = 'Update locations'
    UPDATE_TAGS = 'Update tags'

    object = get_one_or_404(Resource, id=ObjectId(object_id), user=request.user, perm='can_edit')

    # doc = ''
    # places = None
    template_info = _template_info(request.REQUEST.get('popup', ''))

    if request.method == 'POST':
        result = request.POST.get('result', '') # or request.POST.get('result', '')
        if result == 'Cancel':
            return resource_edit_complete(request, object, template_info)
        resourceform = ShortResourceForm(request.POST, instance=object)
        eventform = EventForm(request.POST, instance=object.calendar_event)
        locationform = LocationUpdateForm(request.POST, instance=object)
        # shelflifeform = ShelflifeForm(request.POST, instance=object)

        if resourceform.is_valid(request.user) and locationform.is_valid() and eventform.is_valid():
            acct = get_account(request.user.id)
            object.locations = locationform.locations
            increment_resource_crud('resouce_edit', account=acct)

            # Event dates
            event_start = eventform.cleaned_data['start']
            if event_start:
                object.calendar_event = CalendarEvent(start=event_start, end=eventform.cleaned_data['end'])
            else:
                object.calendar_event = None
            object = resourceform.save(do_save=False)            
            try:
                object.save(author=acct, reindex=True)
                return resource_edit_complete(request, object, template_info)
            except OperationError:
                pass
    else:
        resourceform = ShortResourceForm(instance=object)
        locationform = LocationUpdateForm(instance=object)
        eventform = EventForm(instance=object.calendar_event)
        # shelflifeform = ShelflifeForm(instance=object)

    return render_to_response(template_name,
        RequestContext( request, { 'template_info': template_info, 'object': object,
            'resourceform': resourceform, 'locationform': locationform, 'eventform': eventform, #'places': places,
            # 'tagsform': tagsform, #'shelflifeform': shelflifeform,
            'UPDATE_LOCS': UPDATE_LOCS, 'UPDATE_TAGS': UPDATE_TAGS  }))

@login_required
def resource_edit_complete(request, resource, template_info):
    """docstring for resource_edit_complete"""
    if resource:
        curations = Curation.objects(owner=resource.owner, resource=resource)
        if curations.count() != 1:
            raise Exception('Resource %s with %s owner Curations' % (resource.id, curations.count()))
        cur = curations[0]
        cur.tags = list(set(resource.tags))
        cur.save()
        popup_url = reverse('resource_popup_close')
        url = reverse('resource', args=[resource.id])
    else: # resource_add cancelled
        popup_url = reverse('resource_popup_cancel')
        url = reverse('resource_find')

    if template_info['popup']:
        return HttpResponseRedirect(popup_url)
    else:
        return HttpResponseRedirect(url)

@user_passes_test(lambda u: u.is_staff)
def resource_remove(request, object_id):
    object = get_one_or_404(Resource, id=ObjectId(object_id), user=request.user, perm='can_delete')
    object.delete()

    user = get_account(request.user.id)
    increment_resource_crud('resouce_remove', account=user)
    return HttpResponseRedirect(reverse('resource_list'))

@cache_control(no_cache=False, public=True, must_revalidate=False, proxy_revalidate=False, max_age=300)
def resource_find(request, template_name='depot/resource_find.html'):
    """docstring for resource_find"""
    results = []
    pt_results = {}
    centre = None
    new_search = False

    result = request.REQUEST.get('result', '')
    if request.method == 'POST' or result:
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('resource_list'))
        form = FindResourceForm(request.REQUEST)
        if form.is_valid():
            user = get_account(request.user.id)

            increment_queries(form.cleaned_data['kwords'], account=user)
            increment_locations(form.cleaned_data['post_code'], account=user)

            for result in form.results:
                resource = get_one_or_404(Resource, id=ObjectId(result['res_id']))
                result['resource'] = resource
                # try:
                #     curation_index, curation = get_curation_for_user_resource(user, resource)
                #     print curation
                # except TypeError:
                #     curation_index = curation = None

                # curation_form = CurationForm(
                #         initial={'outcome': STATUS_OK},
                #         instance=curation)
                # resource_report_form = ResourceReportForm()
                # results.append({
                #     'resource_result': result,
                #     'curation': curation,
                #     'curation_form': curation_form,
                #     'resource_report_form': resource_report_form,
                #     'curation_index': curation_index
                # })
                if 'pt_location' in result:
                    pt_results.setdefault(tuple(result['pt_location'][0].split(', ')), []).append((result['res_id'], result['title']))
            centre = form.centre
    else:
        form = FindResourceForm(initial={'boost_location': settings.SOLR_LOC_BOOST_DEFAULT})
        new_search = True

    # hack cos map not showing if no centre point
    # map should show if pt_results anyway, but not happening
    # see also accounts.view.accounts_find

    # just north of Perth
    default_centre = {'location': ('56.5', '-3.5')}

    context = {
        'next': urlquote_plus(request.get_full_path()),
        'form': form,
        'results': form.results,
        'pt_results': pt_results,
        'centre': centre or default_centre if pt_results else None,
        'google_key': settings.GOOGLE_KEY,
        'show_map': pt_results,
        'new_search': new_search
    }
    return render_to_response(template_name, RequestContext(request, context))

def resource_tagged(request, object_id, template_name=''):
    pass
    
def curation_detail(request, object_id, index=None, template_name='depot/curation_detail.html'):
    """docstring for curation_detail"""
    if index:
        resource = get_one_or_404(Resource, id=ObjectId(object_id))
        curation = resource.curations[int(index)]
    else:
        curation = get_one_or_404(Curation, id=ObjectId(object_id))
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
            'url': reverse('curation_add', args=(resource.id, )),
        }
        return HttpResponse(json.dumps(context), mimetype='application/json')

    context = {
        'index': index,
        'object': curation,
        'resource': resource,
    }
    return render_to_response(template_name, RequestContext(request, context))


@login_required
def curation_add(request, object_id, template_name='depot/curation_edit.html'):
    """docstring for curation_add"""
    resource = get_one_or_404(Resource, id=ObjectId(object_id))
    user = get_account(request.user.id)

    curation = get_curation_for_acct_resource(user, resource)
    if curation:
        index, cur = curation
        messages.warning(request, 'You already have a curation for this resource- you can edit it if you need to make changes.')
        return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))

    if request.method == 'POST':
        result = request.POST.get('result', '')
        next = request.GET.get('next', '')
        if next:
            url = '%s#res_%s' % (next, resource.id)
        else:
            url = ''
        if result == 'Cancel':
            return HttpResponseRedirect(url or reverse('resource', args=[resource.id]))
        form = CurationForm(request.POST)
        if form.is_valid(request.user):
            curation = Curation(**form.cleaned_data)
            curation.owner = user
            curation.item_metadata.update(author=user)
            add_curation(resource, curation)
            # TODO: move this into resource.add_curation
            increment_resource_crud('curation_add', account=user)
            index = len(resource.curations) - 1
            return HttpResponseRedirect(url or reverse('curation', args=[resource.id, index]))
    else:
        initial = { 'outcome': STATUS_OK}
        form = CurationForm(initial=initial)

    template_context = {
        'next': urlquote_plus(request.GET.get('next', '')),
        'form': form,
        'resource': resource,
        'new': True
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@login_required
def curation_edit(request, object_id, index, template_name='depot/curation_edit.html'):
    """Curation is an EmbeddedDocument, so can't be saved, needs to be edited, then Resource saved."""
    resource = get_one_or_404(Resource, id=ObjectId(object_id))
    object = resource.curations[int(index)]
    if not request.user.has_perm('can_edit', object):
        raise PermissionDenied()

    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))
        form = CurationForm(request.POST, instance=object)
        if form.is_valid(request.user):
            user = get_account(request.user.id)
            curation = form.save(do_save=False)
            curation.item_metadata.update(author=user)
            curation.save()
            increment_resource_crud('curation_edit', account=user)
            # reload the resource, don't know why, but needed for mongoengine 0.6
            resource = Resource.objects.get(id=resource.id)
            if curation.owner == resource.owner:
                resource.tags = list(set(curation.tags))
            resource.save(reindex=True)
            return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))
    else:
        form = CurationForm(instance=object)

    template_context = {
        'form': form,
        'object': object,
        'resource': resource,
        'new': False
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@login_required
def curation_remove(request, object_id, index):
    """docstring for curation_remove"""
    user = get_account(request.user.id)
    resource = get_one_or_404(Resource, id=ObjectId(object_id), user=request.user, perm='can_delete')
    if resource.owner == resource.curations[int(index)].owner:

        messages.warning(request, 'You cannot delete the curation by the resource owner.')
        return HttpResponseRedirect(reverse('curation', args=[resource.id, index]))

    resource.curations[int(index)].delete()
    del resource.curations[int(index)]
    resource.save(reindex=True)

    increment_resource_crud('curation_remove', account=user)
    return HttpResponseRedirect(reverse('resource', args=[resource.id]))

@login_required
def location_remove(request, object_id, index):
    """docstring for location_remove"""
    resource = get_one_or_404(Resource, id=ObjectId(object_id), user=request.user, perm='can_edit')
    del resource.locations[int(index)]
    resource.save(author=get_account(request.user.id), reindex=True)
    return HttpResponseRedirect(reverse('resource_edit', args=[resource.id]))

def curations_for_group(request, object_id, template_name='depot/curations_for_group.html'):
    """docstring for curations_for_group"""
    object = get_one_or_404(Account, id=ObjectId(object_id))

    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    template_context = {'object': object, 'curations': curations}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

def curations_for_group_html(request, object_id, template_name='depot/curations_for_group_embed.html'):

    object = get_one_or_404(Account, id=ObjectId(object_id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    template_context = {'object': object, 'curations': curations}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

def curations_for_group_js(request, object_id, template_name='depot/curations_for_group_embed.js'):

    object = get_one_or_404(Account, id=ObjectId(object_id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    base_url = Site.objects.get_current().domain
    print base_url
    template_context = Context(
        {'object': object, 'curations': curations, 'base_url': 'http://%s' % base_url})

    response = HttpResponse(mimetype='text/javascript')
    t = loader.get_template(template_name)
    response.write(t.render(template_context))
    return response

def get_curation_for_acct_resource(acct, resource):
    # check if user already has a curation for this resource

    # TODO use resource.get_curation_for_user instead
    if acct:
        for index, cur in enumerate(resource.curations):
            if cur.owner.id == acct.id:
                return index, cur
    return None


