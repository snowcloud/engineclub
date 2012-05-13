from datetime import datetime
from dateutil import parser

from django.core.urlresolvers import reverse
from django.template import Library, Node, Variable
from django.template.defaultfilters import date

from accounts.models import get_account
from issues.models import Issue
from resources.views import get_curation_for_acct_resource

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

def _event_date(value):
    dt = parser.parse(value)
    return date(dt).replace(', 00:00', '')

@register.filter
def idx_event_start(value, arg=None):
    if value.get('event_start', None):
        return _event_date(value['event_start'])
    else:
        return ''

@register.filter
def idx_event_end(value, arg=None):
    if value.get('event_end', None):
        return _event_date(value['event_end'])
    else:
        return ''

@register.filter
def is_owner(user, resource):
    return get_account(user.id) == resource.owner

@register.filter
def issue_status(resource):
    result = -1
    for issue in Issue.objects(related_document=resource, resolved=0):
        result = issue.severity if issue.severity > result else result
    return result

@register.filter
def status_text(resource):
    STATUSES = ['', '', 'serious', 'very serious']
    return STATUSES[issue_status(resource)]

@register.filter
def curation_for_user(resource, user):
    acct = get_account(user.id)
    return get_curation_for_acct_resource(acct, resource)

@register.filter
def search_url(obj, tag):
    if obj.locations:
        loc = obj.locations[0].postcode or obj.locations[0].place_name
    else:
        loc = ''
    if hasattr(obj, 'owner'):
        url_name = 'resource_find'
    else:
        url_name = 'accounts_find'
    return '%s?kwords=%s&post_code=%s&result=Find+items' % (reverse(url_name), tag, loc)

