# stories_tags.py

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe

from resources.models import Curation

register = Library()

@register.inclusion_tag('stories/stories_carousel.html')
def carousel():
    objects = Curation.objects(tags=settings.STORY_TAG)
    return {'objects': objects}
