from django.template import Library, Node, Variable
from django.template.defaultfilters import date

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
        return value['event_start']
    else:
        return ''
