from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from firebox.views import reindex_resources

@user_passes_test(lambda u: u.is_staff)
def index(request):
    
    return render_to_response('enginecab/index.html', RequestContext(request))


@user_passes_test(lambda u: u.is_staff)
def reindex(request):
    
    reindex_resources(settings.MONGO_DB)
    messages.success(request, 'Resources have been reindexed.')
    return HttpResponseRedirect(reverse('cab'))