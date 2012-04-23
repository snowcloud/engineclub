# Create your views here.

from django.conf import settings
# from django.contrib.flatpages.models import Flatpage
from django.shortcuts import render_to_response
from django.template import RequestContext
from pymongo.objectid import ObjectId

from ecutils.utils import get_one_or_404
from resources.models import Resource, Curation
from resources.search import find_by_place_or_kwords

def stories_list(request, template_name='stories/stories_list.html'):
    # flatpages = Flatpage.objects.filter(id=1)
    objects = Curation.objects(tags=settings.STORY_TAG)
    template_context = {'objects': objects}
    # print 'stories:', len(objects)
    return render_to_response(template_name, RequestContext(request, template_context))

def stories_detail(request, object_id, template_name='stories/stories_detail.html'):

    object = get_one_or_404(Curation, id=ObjectId(object_id))
    template_context = {'object': object}
    return render_to_response(template_name, RequestContext(request, template_context))
