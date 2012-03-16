from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.forms import AccountForm, NewAccountForm
from accounts.models import Account
from depot.models import Curation
from ecutils.utils import get_one_or_404
from issues.context_processors import message_stats

@login_required
def index(request):

    if message_stats(request)['message_count']:
        return alerts(request)
    else:
        return account(request)


@login_required
def account(request, template_name='youraliss/account.html'):    

    object =  get_one_or_404(Account, local_id=str(request.user.id))
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=object)
        if form.is_valid():
            g = form.save(True)
            messages.success(request, 'Changes saved.')
            return HttpResponseRedirect(reverse('youraliss-account'))
    else:
        form = AccountForm(instance=object)
    
    template_context = {'form': form, 'new': False, 'object': object}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

# @login_required
# def alerts(request, template_name='youraliss/alerts.html'):    
#     return render_to_response(template_name, RequestContext(request, {}))

@login_required
def curations(request, template_name='youraliss/curations.html'):
    object =  get_one_or_404(Account, local_id=str(request.user.id))
    curations = [c.resource for c in Curation.objects(owner=object).order_by('-item_metadata__last_modified')[:10]]
    template_context = {'object': object, 'curations': curations}
    return render_to_response(template_name, RequestContext(request, template_context))

@login_required
def groups(request, template_name='youraliss/groups.html'):    
    return render_to_response(template_name, RequestContext(request, {}))

