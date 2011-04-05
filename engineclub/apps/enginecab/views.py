from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from firebox.views import reindex_resources

@login_required
def index(request):
    
    return render_to_response('enginecab/index.html', RequestContext(request))


@login_required
def reindex(request):
    
    reindex_resources(settings.MONGO_DB)
    messages.success(request, 'Resources have been reindexed.')
    return HttpResponseRedirect(reverse('cab'))