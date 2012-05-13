from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404

from mongoengine.base import ValidationError
from mongoengine.queryset import OperationError, MultipleObjectsReturned, DoesNotExist

def get_one_or_404(obj_class, **kwargs):
    """helper function for Mongoengine documents"""
    try:
       user = kwargs.pop('user', None)
       perm = kwargs.pop('perm', None)
       object = obj_class.objects.get(**kwargs)
       if user and perm:
           if not user.has_perm(perm, object):
               raise PermissionDenied()
       return object
    except (MultipleObjectsReturned, ValidationError, DoesNotExist):
        raise Http404

def minmax(min, max, v, default=None):
    """ensure v is >= min and <= max"""
    if v is None:
        v = default
    if v < min:
        return min
    elif v > max:
        return max
    else:
        return v

def dict_to_string_keys(d):
    result = {}
    for k,v in d.iteritems():
        result[str(k)] = v
    return result

def lat_lon_to_str(loc):
    """docstring for lat_lon_to_str"""
    if loc:
        if hasattr(loc, 'lat_lon'):
            return (settings.LATLON_SEP).join([unicode(loc.lat_lon[0]), unicode(loc.lat_lon[1])])
        return (settings.LATLON_SEP).join([unicode(loc[0]), unicode(loc[1])])
    else:
        return ''

def get_pages(request, queryset, num=10):
    # all_objects = doc.objects.all()
    paginator = Paginator(queryset, num)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)
    if paginator.num_pages < 9:
      paginator.p_display = 0
      paginator.p_current = range(1,paginator.num_pages+1)
    elif objects.number < 5:
      paginator.p_display = 1
      paginator.p_current = range(1,5) if objects.number != 4 else range(1,6)
      paginator.p_end = range(paginator.num_pages-1, paginator.num_pages+1)
    elif objects.number > paginator.num_pages -4:
      paginator.p_display = 2
      paginator.p_start = range(1,3)
      paginator.p_current = \
          range(paginator.num_pages -3,paginator.num_pages+1) \
          if objects.number != paginator.num_pages -3 else range(paginator.num_pages -4,paginator.num_pages+1)
      # paginator.p_end = range(paginator.num_pages-1, paginator.num_pages+1)
    else:
      paginator.p_display = 3
      paginator.p_start = range(1,3)
      paginator.p_current = \
          range(objects.number - 2, objects.number + 3) \
          # if objects.number != paginator.num_pages -3 else range(paginator.num_pages -4,paginator.num_pages+1)
      paginator.p_end = range(paginator.num_pages-1, paginator.num_pages+1)
      paginator.show_ellipsis1 = objects.number - 2 > 3
      paginator.show_ellipsis2 = paginator.num_pages-1 > objects.number + 3

    return objects
