from django.core.exceptions import PermissionDenied
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