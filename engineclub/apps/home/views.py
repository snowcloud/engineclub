from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext 

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('youraliss'))
    return home(request)

def home(request):
    return render_to_response('home/index.html', RequestContext( request))

