from django.conf import settings
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
from pymongo.objectid import ObjectId

from accounts.models import Account, Collection, get_account
from analytics.shortcuts import (increment_queries, increment_locations,
    increment_resources, increment_resource_crud)
from ecutils.utils import get_one_or_404
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
def detail(request, object_id, template_name='accounts/detail.html'):
    account = get_one_or_404(Account, id=object_id)
    user = request.user
    
    return render_to_response(
        template_name,
        {'object': account},
        RequestContext(request)
    )

@cache_control(no_cache=False, public=True, must_revalidate=False, proxy_revalidate=False, max_age=300)
def accounts_find(request, template_name='accounts/accounts_find.html'):
    """docstring for accounts_find"""
    results = []
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
                resource = get_one_or_404(Account, id=ObjectId(result['res_id']))

                results.append({
                    'resource_result': result,
                    # 'resource_report_form': resource_report_form,
                })
            centre = form.centre
    else:
        form = FindAccountForm(initial={'boost_location': settings.SOLR_LOC_BOOST_DEFAULT})
        new_search = True

    print form

    context = {
        'next': urlquote_plus(request.get_full_path()),
        'form': form,
        'results': results,
        'centre': centre,
        'google_key': settings.GOOGLE_KEY,
        'show_map': results and centre,
        'new_search': new_search
    }
    return render_to_response(template_name, RequestContext(request, context))


 
@login_required
def edit(request, object_id, template_name='accounts/edit.html', next='accounts_detail'):

    account = get_one_or_404(Account, id=object_id)
    user = request.user
    if not (user.is_staff or account.local_id == str(user.id)):
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            g = form.save(True)
            return HttpResponseRedirect(reverse(next, args=[account.id]))
    else:
        form = AccountForm(instance=account)
    
    template_context = {'form': form, 'object': account, 'new': False}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@user_passes_test(lambda u: u.is_staff)
def add(request, template_name='accounts/edit.html', next='cab_user_detail'):
    
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
