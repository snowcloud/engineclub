from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from pymongo.objectid import ObjectId
from pysolr import Solr

from resources.models import Resource, Curation, ItemMetadata, STATUS_OK #, TempCuration
from accounts.models import Account, Collection
from accounts.views import list_detail as def_list_detail, \
    detail as account_detail, edit as account_edit, new as account_add
from ecutils.utils import get_one_or_404
from issues.models import Issue
from issues.views import issue_detail as def_issue_detail


@user_passes_test(lambda u: u.is_staff)
def alerts(request, template_name='enginecab/alerts.html'):    
    context = {}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def resources(request, template_name='enginecab/resources.html'):    
    context = {}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def users(request, template_name='enginecab/users.html'):
    context = {'objects': Account.objects.all()[:40]}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def user_detail(request, object_id, template_name='enginecab/user_detail.html'):
    object = get_one_or_404(Account, id=ObjectId(object_id))
    return account_detail(request, object.id, template_name)

@user_passes_test(lambda u: u.is_staff)
def user_edit(request, object_id, template_name='enginecab/user_edit.html'):
    object = get_one_or_404(Account, id=ObjectId(object_id))
    return account_edit(request, object.id, template_name, next='cab_user_detail')

@user_passes_test(lambda u: u.is_staff)
def user_add(request, template_name='enginecab/user_edit.html'):
    return account_add(request, template_name, next='cab_user_detail')

@user_passes_test(lambda u: u.is_staff)
def reindex(request, template_name=''):
    reindex_resources()
    messages.success(request, 'Resources have been reindexed.')
    return HttpResponseRedirect(reverse('cab_resources'))

@user_passes_test(lambda u: u.is_staff)
def issues(request, template_name='enginecab/issues.html'):
    context = {'objects': Issue.objects.all()}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def issue_detail(request, object_id, template_name='enginecab/issue_detail.html'):
    return def_issue_detail(request, object_id, template_name=template_name, next='cab_issue_detail')
    # object = get_one_or_404(Issue, id=ObjectId(object_id))
    # context = {'object': object}
    # return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def lists(request, template_name='enginecab/lists.html'):
    context = {'objects': Collection.objects.all()}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_staff)
def list_detail(request, object_id, template_name='enginecab/list_detail.html'):
    return def_list_detail(request, object_id, template_name=template_name)
    # object = get_one_or_404(Collection, id=ObjectId(object_id))
    # context = {'object': object}
    # return render_to_response(template_name, RequestContext(request, context))

def reindex_resources(url=settings.SOLR_URL, printit=False):
    """docstring for reindex_resources"""
    # logger.error("indexing resources:")

    from resources.models import Resource

    if printit:
        print 'CLEARING SOLR INDEX: ', url
    conn = Solr(url)
    conn.delete(q='*:*')
    batch_size = getattr(settings, 'SOLR_BATCH_SIZE', 100)
    if printit:
        print 'Indexing %s Resources... (batch: %s)' % (Resource.objects.count(), batch_size)
    
    docs = []
    for i, res in enumerate(Resource.objects):
        entry = res.index()
        if entry:
            docs.extend(entry)
        if i % batch_size == 0:
            conn.add(docs)
            docs = []
    conn.add(docs)


# UTILITY FUNCTIONS

@user_passes_test(lambda u: u.is_staff)
def one_off_util(request):
    # note = 'Nothing enabled.'
    note = migrate_account_collections()
    messages.success(request, 'job done. %s' % note)
    
    return HttpResponseRedirect(reverse('cab_resources'))

def migrate_account_collections():
    # from accounts.models import Account
    for acct in Account.objects.all():
        if acct.in_collections:
            print 'yup', acct.id
            acct.in_collections = acct.collections
            acct.collections = None
            acct.save()
    return 'migrated account collection'
    

# @user_passes_test(lambda u: u.is_staff)
# def show_curationless_resources(request):
#     i = 0
#     r = []
#     for res in Resource.objects.all():
#         if not res.curations:
#             r.append('<a href="/depot/resource/%s">%s</a>' % (res._id, res.title))
#             i += 1
#     note = 'found %s resources with no curations: %s' % (i, ', '.join(r))
#     messages.success(request, 'job done. %s' % note)
    
#     return HttpResponseRedirect(reverse('cab'))

# @user_passes_test(lambda u: u.is_staff)
# def fix_curationless_resources(request):
#     i = 0
#     r = []
#     for res in Resource.objects.all():
#         if not res.curations:
#             obj = Curation(outcome=STATUS_OK, tags=res.tags, owner=res.owner)
#             obj.item_metadata.author = res.owner
#             obj.resource = res
#             obj.save()
#             res.curations.append(obj)
#             res.save(reindex=True)
            
#             r.append('<a href="http://127.0.0.1:8080/depot/resource/%s">%s</a>' % (res._id, res.title))
#             i += 1
            
#     note = 'fixed %s resources with no curations: %s' % (i, ', '.join(r))
#     messages.success(request, 'job done. %s' % note)
    
#     return HttpResponseRedirect(reverse('cab'))
    
# @user_passes_test(lambda u: u.is_staff)
# def remove_dud_curations(request):
#     """docstring for remove_dud_curations"""
#     i = 0
#     for c in Curation.objects.all():
#         try:
#             if not c in c.resource.curations:
#                 # c points to resource, but c not in resource.curations = orphan
#                 c.delete()
#                 i += 1
#         except AttributeError:
#             # c.resource can't be dereferenced, ie ref doesn't exist
#             c.delete()
#             i += 1
#     # return i
    
#     note = 'removed %s dud curations- do a reindex now, will find/fix errors in curations.' % i
#     messages.success(request, 'job done. %s' % note)
    
#     return HttpResponseRedirect(reverse('cab'))
    
# def link_curations_to_resources():
#     """docstring for link_curations_to_resources"""
#     for res in Resource.objects.all():
#         for cur in res.curations:
#             cur.resource = res
#             cur.save()

# def make_tempcurations():
#     """docstring for make_temp_curations"""
#     for res in Resource.objects.all():
#         if res.curations:
#             res.tempcurations = []
#             for cur in res.curations:
#                 res.tempcurations.append(make_tempcuration(cur))
#             if len(res.tempcurations) != len(res.curations):
#                 raise Exception('bummer in %s' % res.id)
#             res.curations = []
#             res.save()
#             print res.id, res.curations, res.tempcurations
#     
# def make_tempcuration(cur):
#     """docstring for mak"""
#     old_im = cur.item_metadata
#     item_metadata = ItemMetadata(
#         last_modified = old_im.last_modified,
#         author = old_im.author,
#         shelflife = old_im.shelflife,
#         status = old_im.status,
#         note = old_im.note,
#     )
#     
#     result = TempCuration(
#         outcome = cur.outcome,
#         tags = cur.tags,
#         # rating - not used
#         note = cur.note,
#         data = cur.data,
#         owner = cur.owner,
#         item_metadata = item_metadata
#     )
#     return result
# 
# def make_newcurations():
#     """docstring for make_temp_curations"""
#     for res in Resource.objects.all():
#         if res.tempcurations:
#             res.curations = []
#             for cur in res.tempcurations:
#                 res.curations.append(make_newcuration(cur))
#             if len(res.tempcurations) != len(res.curations):
#                 raise Exception('bummer in %s' % res.id)
#             
#             res.tempcurations = []
#             res.save()
#             # print res.id, res.curations, res.tempcurations
#     
# def make_newcuration(cur):
#     """docstring for mak"""
#     old_im = cur.item_metadata
#     item_metadata = ItemMetadata(
#         last_modified = old_im.last_modified,
#         author = old_im.author,
#         shelflife = old_im.shelflife,
#         status = old_im.status,
#         note = old_im.note,
#     )
#     
#     result = Curation(
#         outcome = cur.outcome,
#         tags = cur.tags,
#         # rating - not used
#         note = cur.note,
#         data = cur.data,
#         owner = cur.owner,
#         item_metadata = item_metadata
#     )
#     result.save()
#     return result
#     
#     
# def reset_GCD_owners(request):
#     """docstring for reset_GCD_owners(request)"""
#     acct = Account.objects.get(name='Grampian Care Data')
#     # print acct
#     for resource in Resource.objects(uri__startswith='http://www.grampian'):
#         # if len(resource.curations) > 1:
#         #     print resource.title
#         resource.owner = acct
#         resource.curations[0].owner = acct
#         resource.save()

# @user_passes_test(lambda u: u.is_staff)
# def fix_resource_accounts(request):
    
#     # fixes = {
#     #     '1': Account.objects.get(id=ObjectId(u'4d9b9a4489cb16665c000002')),
#     #     # '2': u'4d9b945f3de074084f000000'
#     # }
    
#     for resource in Resource.objects.all():
#         # local_id = resource.item_metadata.author
#         try:
#             # acct = fixes.get(local_id, None)
#             # if acct is None:
#             #     # can't just use setdefault, cos evaluates queryset every time
#             #     acct = fixes.setdefault(local_id, Account.objects.get(local_id=local_id))
#             # # print local_id, acct_id
#             # if resource.owner is None:
#             #     resource.owner = acct
#             acct = resource.owner
#             if acct is None:
#                 raise Exception('no owner for resource: %s, %s' % (resource.title, resource.id))
#             # set item metadata
#             resource.item_metadata.author = acct
#             # set moderation
#             for obj in resource.moderations:
#                 obj.owner = acct
#                 obj.item_metadata.author = acct
#             # set curations
#             for obj in resource.curations:
#                 obj.owner = acct
#                 obj.item_metadata.author = acct
            
#             resource.save()
#         except Account.DoesNotExist:
#             print fixes[local_id]
#             print local_id, resource.title
#             print fixes
#             raise Exception('stop it.')   
        
#     print 'done' #, fixes
#     # for u in User.objects.all():
#     #     print u.id
                
#     return HttpResponseRedirect(reverse('cab'))

# @user_passes_test(lambda u: u.is_staff)
# def fix_urls(request):
#     for resource in Resource.objects(uri__startswith='http://new.gramp'):
#         resource.uri = resource.uri.replace('//new.', '//www.')
#         resource.save()
        
#     messages.success(request, 'URLs have been fixed.')
    
#     return HttpResponseRedirect(reverse('cab'))
