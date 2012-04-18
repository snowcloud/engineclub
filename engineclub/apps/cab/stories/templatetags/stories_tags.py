# stories_tags.py

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_filter
def story_pic(value):
	return '/'
