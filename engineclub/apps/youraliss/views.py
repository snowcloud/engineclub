from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.forms import AccountForm, NewAccountForm
from accounts.views import get_one_or_404
from notifications.context_processors import notifications

@login_required
def index(request):

    if notifications(request)['notifications_count']:
        return alerts(request)
    else:
        return account(request)


@login_required
def account(request, template_name='youraliss/account.html'):    

    object =  get_one_or_404(local_id=str(request.user.id))
    
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

@login_required
def alerts(request):    
    return render_to_response('youraliss/alerts.html', RequestContext(request, {}))

@login_required
def curations(request):    
    return render_to_response('youraliss/curations.html', RequestContext(request, {}))

@login_required
def groups(request):    
    return render_to_response('youraliss/groups.html', RequestContext(request, {}))

