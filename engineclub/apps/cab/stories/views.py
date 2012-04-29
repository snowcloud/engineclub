# Create your views here.

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from pymongo.objectid import InvalidId, ObjectId

from ecutils.forms import FileUploadForm
from ecutils.utils import get_one_or_404
from accounts.models import Account
from resources.models import Resource, Curation
from resources.search import find_by_place_or_kwords

def get_story(obj, story_type):
    if story_type == 'curation':
        return {
            'obj': obj,
            'id': obj.id,
            'type': 'curation',
            'title': obj.resource.title,
            'url': reverse('stories_detail', args=[obj.id]),
            'source_url': reverse('resource', args=[obj.resource.id]),
            'content': obj.note }
    elif story_type == 'account':
        return {
            'id': obj.id,
            'type': 'account',
            'title': obj.name,
            'url': reverse('stories_detail', args=[obj.id]),
            'source_url': reverse('accounts_detail', args=[obj.id]),
            'content': obj.description }
    elif story_type == 'flatpage':
        return {
            'id': obj.id,
            'type': 'flatpage',
            'title': obj.title,
            'url': reverse('stories_detail', args=[obj.id]),
            'source_url': obj.url,
            'content': obj.content }
    else:
        raise Exception('unknown story type')

def get_stories():
    objects = [get_story(obj, 'curation') for obj in Curation.objects(tags=settings.STORY_TAG)]
    objects.extend([get_story(obj, 'account') for obj in Account.objects(tags=settings.STORY_TAG)])
    objects.extend([get_story(obj, 'flatpage') for obj in FlatPage.objects.filter(url__startswith='/story/')])
    return objects

def stories_list(request, template_name='stories/stories_list.html'):

    # fetch all story objects: Curations, Accounts, Flatpages
    # populate list of dictionaries in objects

    template_context = {'objects': get_stories()}
    return render_to_response(template_name, RequestContext(request, template_context))

def handle_uploaded_file(f, object_id):
    f_name = '%s/images/stories/%s.jpg' % (settings.MEDIA_ROOT, object_id)
    destination = open(f_name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

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

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['picture_file'], object.id)
    else:
        form = FileUploadForm(initial={'picture_file': 'blah/de/blah.jpg'})

    template_context = {'object': get_story(object, obj_type), 'form': form}
    return render_to_response(template_name, RequestContext(request, template_context))





