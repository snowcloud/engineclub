from datetime import datetime
from dateutil import parser

from django.template import Library, Node, Variable
from django.template.defaultfilters import date

from accounts.models import get_account
from issues.models import Issue

register = Library()

@register.simple_tag
def site_base():
    return Site.objects.get_current().domain

@register.filter
def event_date(value, arg=None):
    """ usage {{ object.calendar_event|event_date }}
    
    """
    def _format_date(d, format=None):
        # uses django date filter, format defaults to settings.DATE_FORMAT
        return  date(d, format).replace(', 00:00', '')

    if value and value.start:
        s = _format_date(value.start)
        e = ' - %s' % _format_date(value.end) if value.end else ''
        return '%s%s' % (s, e)
    else:
        return ''

@register.filter
def idx_event_date(value, arg=None):
    if value.get('event_start', None):
        dt = parser.parse(value['event_start'])
        return date(dt).replace(', 00:00', '')
    else:
        return ''

@register.filter
def is_owner(user, resource):
    return get_account(user.id) == resource.owner

@register.filter
def status(resource):
    result = -1
    for issue in Issue.objects(related_document=resource):
        result = issue.severity if issue.severity > result else result
    return result

@register.filter
def status_text(resource):
    STATUSES = ['', '', 'serious', 'very serious']
    return STATUSES[status(resource)]
