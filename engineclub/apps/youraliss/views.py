from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext


@login_required
def account(request):    
    return render_to_response('youraliss/account.html', RequestContext(request, {}))

@login_required
def alerts(request):    
    return render_to_response('youraliss/alerts.html', RequestContext(request, {}))

@login_required
def curations(request):    
    return render_to_response('youraliss/curations.html', RequestContext(request, {}))

@login_required
def groups(request):    
    return render_to_response('youraliss/groups.html', RequestContext(request, {}))

