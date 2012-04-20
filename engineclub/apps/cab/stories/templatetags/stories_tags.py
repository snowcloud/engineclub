# stories_tags.py

import os

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe

from resources.models import Curation

register = Library()

@register.inclusion_tag('stories/stories_carousel.html')
def carousel():
    objects = Curation.objects(tags=settings.STORY_TAG)
    return {'objects': objects}

@register.filter
def pic(value, size):
	path = '%s/images/stories/%s.jpg' % (settings.MEDIA_ROOT, value)
	if os.path.exists(path):
		return '%simages/stories/%s.jpgx' % (settings.MEDIA_URL, value)
	return 'http://placekitten.com/%s' % '/'.join(size.split(','))
