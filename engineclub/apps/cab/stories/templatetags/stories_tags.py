# stories_tags.py

import os

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe

from stories.views import get_stories

register = Library()

@register.inclusion_tag('stories/stories_carousel.html')
def carousel():
    return {'objects': get_stories()}

@register.filter
def pic(value, size):
	path = '%s/images/stories/%s.jpg' % (settings.MEDIA_ROOT, value)
	if os.path.exists(path):
		return '%simages/stories/%s.jpg' % (settings.MEDIA_URL, value)
	return 'http://placekitten.com/%s' % '/'.join(size.split(','))
