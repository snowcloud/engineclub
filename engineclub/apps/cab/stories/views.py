# Create your views here.

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from pymongo.objectid import InvalidId, ObjectId

from ecutils.utils import get_one_or_404
from accounts.models import Account
from resources.models import Resource, Curation
from resources.search import find_by_place_or_kwords

def stories_list(request, template_name='stories/stories_list.html'):

    # fetch all story objects: Curations, Accounts, Flatpages
    # populate list of dictionaries in objects

    # TESTS !!!

    objects = [{
            'id': obj.id,
            'type': 'curation',
            'title': obj.resource.title,
            'url': reverse('stories_detail', args=[obj.id]),
            'content': obj.note } for obj in Curation.objects(tags=settings.STORY_TAG)]
    objects.extend([{
            'id': obj.id,
            'type': 'account',
            'title': obj.name,
            'url': reverse('stories_detail', args=[obj.id]),
            'content': obj.description } for obj in Account.objects(tags=settings.STORY_TAG)])
    objects.extend([{
            'id': obj.id,
            'type': 'flatpage',
            'title': obj.title,
            'url': reverse('stories_detail', args=[obj.id]),
            # 'url': obj.url,
            'content': obj.content } for obj in FlatPage.objects.filter(url__startswith='/story/')])
    template_context = {'objects': objects}
    return render_to_response(template_name, RequestContext(request, template_context))

def stories_detail(request, object_id, template_name='stories/stories_detail.html'):

    try:
        object = Curation.objects.get(pk=ObjectId(object_id))
        obj_type = 'curation'
    except Curation.DoesNotExist:
        object = get_one_or_404(Account, id=ObjectId(object_id))
        obj_type = 'account'
    except InvalidId:
        object = FlatPage.objects.get(pk=object_id)
        obj_type = 'flatpage'
    template_context = {'object': object, 'obj_type': obj_type}
    return render_to_response(template_name, RequestContext(request, template_context))
