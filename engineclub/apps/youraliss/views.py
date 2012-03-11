from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from engine_groups.forms import AccountForm, NewAccountForm
from engine_groups.views import get_one_or_404

@login_required
def account(request, template_name='youraliss/account.html'):    

    print request.user.id
    
    object =  get_one_or_404(local_id=str(request.user.id))
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=object)
        if form.is_valid():
            g = form.save()
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

