from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from depot.models import Resource
from firebox.views import reindex_resources
from engine_groups.models import Account
from pymongo.objectid import ObjectId


@user_passes_test(lambda u: u.is_staff)
def index(request):
    
    return render_to_response('enginecab/index.html', RequestContext(request))


@user_passes_test(lambda u: u.is_staff)
def reindex(request):
    
    reindex_resources(settings.MONGO_DB)
    messages.success(request, 'Resources have been reindexed.')
    return HttpResponseRedirect(reverse('cab'))
    
@user_passes_test(lambda u: u.is_staff)
def fix_resource_accounts(request):
    
    fixes = {
        '1': Account.objects.get(id=ObjectId(u'4d9b945f3de074084f000000')),
        # '2': u'4d9b945f3de074084f000000'
    }
    
    for resource in Resource.objects.all():
        local_id = resource.item_metadata.author
        try:
            acct = fixes.get(local_id, None)
            if acct is None:
                # can't just use setdefault, cos evaluates queryset every time
                acct = fixes.setdefault(local_id, Account.objects.get(local_id=local_id))
            # print local_id, acct_id
            if resource.owner is None:
                resource.owner = acct
                resource.save()
        except Account.DoesNotExist:
            print fixes[local_id]
            print local_id, resource.title
            print fixes
            raise Exception('stop it.')   
        
    print 'done', fixes
    # for u in User.objects.all():
    #     print u.id
        
        
    return HttpResponseRedirect(reverse('cab'))
    