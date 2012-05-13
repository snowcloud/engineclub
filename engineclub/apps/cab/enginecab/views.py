from datetime import datetime
from urllib import unquote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from bson.objectid import ObjectId
from pysolr import Solr

from resources.models import Resource, Curation, ItemMetadata, STATUS_OK #, TempCuration
from accounts.models import Account, Collection
from accounts.views import list_detail as def_list_detail, \
    detail as accounts_detail, edit as account_edit, add as account_add
from ecutils.models import Setting
from ecutils.utils import get_one_or_404
from enginecab.forms import TagsFixerForm, UPPERCASE
from enginecab.models import TagProcessor
from issues.models import Issue
from issues.views import issue_detail as def_issue_detail
from locations.forms import LocationSearchForm, LocationEditForm
from locations.models import Location


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
    return accounts_detail(request, object.id, template_name)

@user_passes_test(lambda u: u.is_staff)
def user_edit(request, object_id, template_name='enginecab/user_edit.html'):
    object = get_one_or_404(Account, id=ObjectId(object_id))
    return account_edit(request, object.id, template_name, next='cab_user_detail')

@user_passes_test(lambda u: u.is_staff)
def user_add(request, template_name='enginecab/user_edit.html'):
    return account_add(request, template_name, next='cab_user_detail')

@user_passes_test(lambda u: u.is_staff)
def reindex(request, template_name=''):
    reindex_accounts()
    messages.success(request, 'Accounts have been reindexed.')
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

@user_passes_test(lambda u: u.is_superuser)
def locations_index(request, template_name='enginecab/locations_index.html'):

    if request.method == 'POST':
        form = LocationSearchForm(request.REQUEST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('cab_locations_detail', args=[form.loc_found['_id']]))
    else:
        form = LocationSearchForm(initial={})

    context = { 'form': form }
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_superuser)
def locations_detail(request, object_id, template_name='enginecab/locations_detail.html'):
    object = get_one_or_404(Location, id=object_id)
    context = {'object': object}
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_superuser)
def locations_add(request, template_name='enginecab/locations_edit.html'):
    from locations.models import ALISS_LOCATION

    if request.method == 'POST':
        result = request.POST.get('result', '')
        if result == 'Cancel':
            return HttpResponseRedirect(reverse('cab_locations'))
        form = LocationEditForm(request.POST)
        if form.is_valid(request.user):
            location = Location(**form.cleaned_data).save()
            return HttpResponseRedirect(reverse('cab_locations_detail', args=[location.id]))
    else:
        initial = {
            'place_name': 'Craigroyston',
            'lat': 55.9736,
            'lon': -3.2541,
            'accuracy': 6,
            'loc_type': ALISS_LOCATION,
            'district': 'City of Edinburgh',
            'country_code': 'SCT'
        }
        form = LocationEditForm(initial=initial)

    template_context = {
        'form': form,
        'new': True
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

@user_passes_test(lambda u: u.is_superuser)
def locations_remove(request, object_id):
    """docstring for location_remove"""
    object = get_one_or_404(Location, id=object_id, user=request.user, perm='can_delete')

    resources = Resource.objects(locations=object)
    accounts = Account.objects(locations=object)
    if resources or accounts:
        res_str = ','.join([res.name for res in resources])
        acct_str = ','.join(['<a href="%s">%s</a>' % (reverse('accounts_edit', args=[acct.id]), acct.name) for acct in accounts])
        messages.error(
            request, 
            'Resources/Accounts using this location:<br>%s<br>%s.' % (res_str, acct_str))
        return HttpResponseRedirect(reverse('cab_locations_detail', args=[object.id]))
    object.delete()
    messages.success(request, 'Location removed')
    return HttpResponseRedirect(reverse('cab_locations'))

@user_passes_test(lambda u: u.is_superuser)
def tags_index(request, template_name='enginecab/tags_index.html'):
    if request.method == 'POST':
        result = request.POST.get('result')
        tag_process = request.POST.get('tag_process')
        form = TagsFixerForm(request.REQUEST)
        if result and form.is_valid():
            tags_process(request, form.cleaned_data)
            return HttpResponseRedirect(reverse('cab_tags'))
        elif tag_process:
            change_tag = request.POST.get('change_tag')
            tag_id = request.POST.get('tag_id')[10:]
            if tag_process == 'upper':
                return tags_upper(request, tag_id)
            elif tag_process == 'lower':
                return tags_lower(request, tag_id)
            elif tag_process == 'remove':
                return tags_remove(request, tag_id)
            elif tag_process == 'change':
                return tags_change(request, tag_id, change_tag)
    else:
        form = TagsFixerForm(initial={})

    context = {
        'objects': sorted(set(
            list(Curation.objects.ensure_index("tags").distinct("tags")) + 
            list(Account.objects.ensure_index("tags").distinct("tags")))),
        'form': form,
        }
    return render_to_response(template_name, RequestContext(request, context))

@user_passes_test(lambda u: u.is_superuser)
def tags_process(request, options):
    results = []
    if options['split'] or options['lower_case']:
        setting, _ = Setting.objects.get_or_create(key=UPPERCASE)
        exceptions = setting.value.get('data', [])
        for obj in Curation.objects():
            tp = TagProcessor(obj.tags)
            obj.tags = tp.split(options['split']).lower(options['lower_case'], exceptions).tags
            obj.save()
        for obj in Account.objects():
            tp = TagProcessor(obj.tags)
            obj.tags = tp.split(options['split']).lower(options['lower_case'], exceptions).tags
            obj.save()
    results.append('done') 
    messages.success(request, '<br>'.join(results))

def alpha_id(object_id):
    return '#alpha_%s' % object_id[0]

@user_passes_test(lambda u: u.is_superuser)
def tags_edit(request, object_id):
    return HttpResponseRedirect('%s%s' % (reverse('cab_tags'), alpha_id(object_id)))

@user_passes_test(lambda u: u.is_superuser)
def tags_upper(request, object_id):
    object_id = unquote(object_id)
    if object_id != object_id.upper():
        curations = Curation.objects.filter(tags=object_id).update(push__tags=object_id.upper())
        curations = Curation.objects.filter(tags=object_id).update(pull__tags=object_id)
    messages.success(request, 'Made %s - %s' % (object_id, object_id.upper()))
    return HttpResponseRedirect('%s%s' % (reverse('cab_tags'), alpha_id(object_id)))

@user_passes_test(lambda u: u.is_superuser)
def tags_lower(request, object_id):
    object_id = unquote(object_id)
    if object_id != object_id.lower():
        curations = Curation.objects.filter(tags=object_id).update(push__tags=object_id.lower())
        curations = Curation.objects.filter(tags=object_id).update(pull__tags=object_id)
    messages.success(request, 'Made %s - %s' % (object_id, object_id.lower()))
    return HttpResponseRedirect('%s%s' % (reverse('cab_tags'), alpha_id(object_id)))

@user_passes_test(lambda u: u.is_superuser)
def tags_change(request, object_id, change_id):
    object_id = unquote(object_id)
    change_id = unquote(change_id)
    if change_id and object_id != change_id:
        curations = Curation.objects.filter(tags=object_id).update(push__tags=change_id)
        curations = Curation.objects.filter(tags=object_id).update(pull__tags=object_id)
        for cur in Curation.objects.filter(tags=change_id):
            cur.resource.reindex()

    messages.success(request, 'Changed %s to %s' % (object_id, change_id))
    return HttpResponseRedirect('%s%s' % (reverse('cab_tags'), alpha_id(object_id)))

@user_passes_test(lambda u: u.is_superuser)
def tags_remove(request, object_id):
    object_id = unquote(object_id)
    curations = Curation.objects.filter(tags=object_id).update(pull__tags=object_id)
    messages.success(request, 'Removed - %s' % object_id)
    return HttpResponseRedirect('%s%s' % (reverse('cab_tags'), alpha_id(object_id)))

def reindex_accounts(url=settings.SOLR_URL, printit=False):
    """docstring for reindex_accounts"""
    # logger.error("indexing accounts:")

    from accounts.models import Account

    if printit:
        print 'CLEARING SOLR INDEX for Accounts: ', url
    conn = Solr(url)
    conn.delete(q='res_type:%s' % settings.SOLR_ACCT)
    batch_size = getattr(settings, 'SOLR_BATCH_SIZE', 100)
    if printit:
        print 'Indexing %s Accounts... (batch: %s)' % (Account.objects.count(), batch_size)
    
    docs = []
    for i, res in enumerate(Account.objects):
        entry = res.index()
        if entry:
            docs.extend(entry)
        if i % batch_size == 0:
            conn.add(docs)
            docs = []
    conn.add(docs)

def reindex_resources(url=settings.SOLR_URL, printit=False):
    """docstring for reindex_resources"""
    # logger.error("indexing resources:")

    from resources.models import Resource

    if printit:
        print 'CLEARING SOLR INDEX for Resources: ', url
    conn = Solr(url)
    conn.delete(q='res_type:%s' % settings.SOLR_RES)
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

@user_passes_test(lambda u: u.is_superuser)
def one_off_util(request):
    note = 'Nothing enabled.'
    # note = move_res_tags_to_owner_curation()
    messages.success(request, 'job done. %s' % note)

    # note = show_curationless_resources()
    # messages.success(request, 'job done. %s' % note)
    # note = fix_curationless_resources()
    # messages.success(request, 'job done. %s' % note)
   
    return HttpResponseRedirect(reverse('cab_resources'))

# def migrate_account_collections():
#     # from accounts.models import Account
#     for acct in Account.objects.all():
#         if acct.collections:
#             # print 'yup', acct.id
#             acct.in_collections = acct.collections
#             acct.collections = None
#             acct.save()
#     return 'migrated account collection- now comment out account.collection field'
    

def show_curationless_resources():
    i = 0
    r = []
    for res in Resource.objects.all():
        if not res.curations:
            r.append('<a href="/depot/resource/%s">%s</a>' % (res._id, res.title))
            i += 1
    return 'found %s resources with no curations: %s' % (i, ', '.join(r))

def fix_curationless_resources():
    i = 0
    r = []
    for res in Resource.objects.all():
        if not res.curations:
            obj = Curation(outcome=STATUS_OK, tags=res.tags, owner=res.owner)
            obj.item_metadata.author = res.owner
            obj.resource = res
            obj.save()
            res.curations.append(obj)
            res.save(reindex=True)
            
            r.append('<a href="http://127.0.0.1:8080/depot/resource/%s">%s</a>' % (res._id, res.title))
            i += 1
            
    return 'fixed %s resources with no curations: %s' % (i, ', '.join(r))

def move_res_tags_to_owner_curation():
    i = 0
    r = []
    # start = datetime.now()

    for res in Resource.objects.all():
        curations = Curation.objects(owner=res.owner, resource=res)
        cur = None
        if curations.count() < 1:
            r.append('<a href="http://127.0.0.1:8080/depot/resource/%s">%s</a>' % (res._id, res.title))

            cur = Curation(outcome=STATUS_OK, tags=res.tags, owner=res.owner)
            cur.item_metadata.author = res.owner
            cur.resource = res
            cur.save()
            res.curations = [cur] + list(res.curations)
            res.save(reindex=True)
            print i, res.curations
            
            i += 1
        # else:
        #     cur = curations[0]
        #     cur.tags = list(set(cur.tags + res.tags))
        #     cur.save()


    # end = datetime.now()
    # print end - start

    return 'found %s resources: %s' % (i, ', '.join(r))


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
