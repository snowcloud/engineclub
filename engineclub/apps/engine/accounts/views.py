from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlquote_plus
from django.views.decorators.cache import cache_control

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist
from bson.objectid import ObjectId

from accounts.models import Account, Collection, get_account
from analytics.shortcuts import (increment_queries, increment_locations,
    increment_resources, increment_resource_crud)
from ecutils.forms import ConfirmForm
from ecutils.utils import get_one_or_404, get_pages

from resources.models import Curation
from resources.forms import LocationUpdateForm
from forms import AccountForm, NewAccountForm, FindAccountForm

# def get_one_or_404(**kwargs):
#     try:
#        object = Account.objects.get(**kwargs)
#        return object
#     except (MultipleObjectsReturned, ValidationError, DoesNotExist):
#         raise Http404
    
def index(request):
    objects = Account.objects
    return render_to_response('accounts/index.html',
        RequestContext( request, { 'objects': objects }))

# @login_required
def detail(request, object_id, template_name='accounts/accounts_detail.html', next=None):
    account = get_one_or_404(Account, id=object_id)
    user = request.user
    pt_results = {}
    centre = None

    if account.locations:
        centre = {'name': unicode(account.locations[0]), 'location': (account.locations[0].lat_lon) }

    # curations = Curation.objects(owner=account).order_by('-item_metadata__last_modified')[:40]
    curations = get_pages(request, Curation.objects(owner=account).order_by('-item_metadata__last_modified'), 20)

    # map has all curations
    for curation in Curation.objects(owner=account):
        for loc in curation.resource.locations:
            pt_results.setdefault(tuple(loc.lat_lon), []).append((curation.resource.id, curation.resource.title))
    context = {
        'curations': curations,
        'curations_count': Curation.objects(owner=account).count(),
        'pt_results': pt_results,
        'centre': centre,
        'google_key': settings.GOOGLE_KEY,
        'show_map': pt_results,
        'next': next or '%s?page=%s' % (reverse('accounts_detail', args=[account.id]), curations.number)
    }
    return render_to_response(
        template_name,
        {'object': account},
        RequestContext(request, context)
    )

@cache_control(no_cache=False, public=True, must_revalidate=False, proxy_revalidate=False, max_age=300)
def accounts_find(request, template_name='accounts/accounts_find.html'):
    """docstring for accounts_find"""
    results = []
    pt_results = {}
    centre = None
    new_search = False

    result = request.REQUEST.get('result', '')
    if request.method == 'POST' or result:
        pass
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('resource_list'))
        form = FindAccountForm(request.REQUEST)
        if form.is_valid():
            user = get_account(request.user.id)

            increment_queries(form.cleaned_data['kwords'], account=user)
            increment_locations(form.cleaned_data['post_code'], account=user)

            for result in form.results:
                acct = get_one_or_404(Account, id=ObjectId(result['res_id']))
                result['resource'] = acct
                results.append({'resource_result': result})
                if 'pt_location' in result:
                    pt_results.setdefault(tuple(result['pt_location'][0].split(', ')), []).append((result['res_id'], result['title']))
            centre = form.centre
    else:
        form = FindAccountForm(initial={'boost_location': settings.SOLR_LOC_BOOST_DEFAULT})
        new_search = True

    # hack cos map not showing if no centre point
    # map should show if pt_results anyway, but not happening
    # see also resources.view.resource_find

    # just north of Perth
    default_centre = {'location': ('56.5', '-3.5')}

    context = {
        'next': urlquote_plus(request.get_full_path()),
        'form': form,
        'results': results,
        'pt_results': pt_results,
        'centre': centre or default_centre if pt_results else None,
        'google_key': settings.GOOGLE_KEY,
        'show_map': pt_results,
        'new_search': new_search
    }
    return render_to_response(template_name, RequestContext(request, context))

@login_required
def edit(request, object_id, template_name='accounts/accounts_edit.html', next='accounts_detail'):

    # object = get_one_or_404(Account, id=object_id)
    object = get_one_or_404(Account, id=ObjectId(object_id), user=request.user, perm='can_edit')
    user = request.user
    if not (user.is_staff or object.local_id == str(user.id)):
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=object)
        locationform = LocationUpdateForm(request.POST, instance=object)
        if form.is_valid(request.user) and locationform.is_valid():
            acct = get_account(request.user.id)

            object.locations = locationform.locations
            object.save()

            increment_resource_crud('account_edit', account=acct)
            object = form.save(False)
            object.save(reindex=True)
            return HttpResponseRedirect(reverse(next, args=[object.id]))
    else:
        form = AccountForm(instance=object)
        locationform = LocationUpdateForm(instance=object)
    
    template_context = {
        'form': form, 'object': object, 
        'locationform': locationform, 'new': False }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@user_passes_test(lambda u: u.is_superuser)
def remove(request, object_id, template_name='ecutils/confirm.html'):
    """docstring for delete"""
    object = get_one_or_404(Account, id=ObjectId(object_id), user=request.user, perm='can_delete')
    user = request.user
    if not (user.is_staff or object.local_id == str(user.id)):
        raise PermissionDenied()

    if request.POST:
        if request.POST['result'] == 'Cancel':
            return HttpResponseRedirect(reverse('accounts_detail', args=[object.id]))
        else:
            form = ConfirmForm(request.POST)
            if form.is_valid():
                object.delete()
                messages.success(request, 'Account has been removed, with any Resources, Curations, Collections and Issues.')
                return HttpResponseRedirect(reverse('accounts'))
    else:
        form = ConfirmForm(initial={ 'object_name': object.name })
    return render_to_response('ecutils/confirm.html', 
        RequestContext( request, 
            {   'form': form,
                'title': 'Delete this user account?'
            })
        )

@user_passes_test(lambda u: u.is_staff)
def add(request, template_name='accounts/accounts_edit.html', next='cab_user_detail'):
    
    if request.method == 'POST':
        form = NewAccountForm(request.POST)
        if form.is_valid():
            account = Account(**form.cleaned_data)
            account.save()
            return HttpResponseRedirect(reverse(next, args=[account.id]))
    else:
        form = NewAccountForm()
    
    template_context = {'form': form, 'new': True}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@login_required
def list_detail(request, object_id, template_name='youraliss/list_detail.html'):
    object = get_one_or_404(Collection, id=ObjectId(object_id))
    context = {'object': object}
    return render_to_response(template_name, RequestContext(request, context))
