from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist
from pymongo.objectid import ObjectId

from accounts.models import Account
from forms import AccountForm, NewAccountForm

def get_one_or_404(**kwargs):
    try:
       object = Account.objects.get(**kwargs)
       return object
    except (MultipleObjectsReturned, ValidationError, DoesNotExist):
        raise Http404
    
def index(request):
    objects = Account.objects
    return render_to_response('accounts/index.html',
        RequestContext( request, { 'objects': objects }))

def detail(request, object_id, template_name='accounts/detail.html'):
    group = get_one_or_404(id=object_id)
    
    return render_to_response(
        template_name,
        {'object': group},
        RequestContext(request)
    )
    
@user_passes_test(lambda u: u.is_staff)
def edit(request, object_id, template_name='accounts/edit.html'):

    object = get_one_or_404(id=object_id)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=object)
        if form.is_valid():
            g = form.save(True)
            return HttpResponseRedirect(reverse('group', args=[object.id]))
    else:
        form = AccountForm(instance=object)
    
    template_context = {'form': form, 'new': False}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@user_passes_test(lambda u: u.is_staff)
def new(request, template_name='accounts/edit.html'):
    
    if request.method == 'POST':
        form = NewAccountForm(request.POST)
        if form.is_valid():
            g = form.save(True)
            return HttpResponseRedirect(reverse('group', args=[g.id]))
    else:
        form = NewAccountForm()
    
    template_context = {'form': form, 'new': True}

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

