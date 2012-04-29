from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.models import Account, Collection
from accounts.views import detail as accounts_detail, edit as account_edit, \
    list_detail as def_list_detail
from resources.models import Curation
from ecutils.utils import get_one_or_404
from issues.context_processors import message_stats

@login_required
def index(request):
    if message_stats(request)['account_message_count']:
        return alerts(request)
    else:
        return account(request)

@login_required
def profile(request, object_id=None, template_name='youraliss/profile.html'):
    object =  get_one_or_404(Account, local_id=str(request.user.id))
    return accounts_detail(request, object.id, template_name)

@login_required
def account(request, template_name='youraliss/account.html'):    
    object =  get_one_or_404(Account, local_id=str(request.user.id))
    return account_edit(request, object.id, template_name, next='youraliss')
    
@login_required
def curations(request, template_name='youraliss/curations.html'):
    object =  get_one_or_404(Account, local_id=str(request.user.id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    template_context = {'object': object, 'curations': curations}
    return render_to_response(template_name, RequestContext(request, template_context))

@login_required
def lists(request, template_name='youraliss/lists.html'):    
    account =  get_one_or_404(Account, local_id=str(request.user.id))
    objects = Collection.objects(owner=account).order_by('-name')
    template_context = {'account': account, 'objects': objects}
    return render_to_response(template_name, RequestContext(request, template_context))

@login_required
def lists_detail(request, object_id, template_name='youraliss/lists_detail.html'):    
    return def_list_detail(request, object_id, template_name)
    # account =  get_one_or_404(Account, local_id=str(request.user.id))
    # objects = Collection.objects(owner=account).order_by('-name')
    # template_context = {'account': account, 'objects': objects}
    # return render_to_response(template_name, RequestContext(request, template_context))

