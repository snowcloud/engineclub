import re

from django.conf import settings
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson as json

from mongoengine import ValidationError #, Q
from mongoengine.connection import _get_db as get_db

from analytics.shortcuts import (increment_api_queries, increment_api_locations,
    increment_api_resources)
from locations.models import Location
from resources.models import Resource, Curation
from resources.search import find_by_place_or_kwords, get_location
increment_api_resources
class JsonResponse(HttpResponse):
    """from http://www.djangosnippets.org/snippets/1639/"""
    errors = {}
    __data = []
    callback = None

    def __set_data(self, data):
        if data == []:
            self.__data = []
        else:
            self.__data = (isinstance(data, QuerySet) or hasattr(data[0], '_meta'))\
                and serializers.serialize('python', data) or data

    data = property(fset = __set_data)

    def __get_container(self):
        content = json.dumps(
            {
                "data": self.__data,
                "errors":self.errors,
            }, cls = DjangoJSONEncoder)
        if self.callback:
            return '%s (%s)' % (self.callback, content)
        else:
            return content

    def __set_container(self, val):
        pass

    _container = property(__get_container, __set_container)

    def __init__(self, *args, **kwargs):
        kwargs["mimetype"] = "application/javascript"

        if "data" in kwargs:
            self.data = kwargs.pop("data")

        if "errors" in kwargs:
            self.errors = kwargs.pop("errors")

        if "callback" in kwargs:
            self.callback = kwargs.pop('callback')

        super(JsonResponse, self).__init__(*args, **kwargs)

def resource_by_id(request, id):
    """docstring for item_resource"""
    callback = request.REQUEST.get('callback')

    errors = []
    try:
        item = Resource.objects.get(id=id)
    except ValidationError:
        result_code = 20
        errors.append('Not a valid resource ID')
    except Resource.DoesNotExist:
        result_code = 20
        errors.append('No resource found with that ID')
    # print item.title

    if errors:
        return JsonResponse(errors={ 'code': result_code, 'message': '. '.join(errors)})

    increment_api_resources(id)

    data=[{
        'id': unicode(item.id),
        'title': item.title,
        'description': item.description,
        'resourcetype': item.resource_type or '',
        'uri': item.uri,
        'locations': ['%s, %s' % (loc.lat_lon[0], loc.lat_lon[1]) for loc in item.locations],
        'locationnames': [loc.place_name for loc in item.locations],
        'event_start': (item.calendar_event.start or '') if item.calendar_event else '',
        'event_end': (item.calendar_event.end or '') if item.calendar_event else '',
        'tags': item.tags,
        'lastmodified': item.item_metadata.last_modified,
    }]
    return JsonResponse(data=data, callback=callback)

def _check_int(i):
    try:
        int(i)
        return True
    except ValueError:
        print i
        return None

def _loc_to_str(loc):
    if loc:
        return ["%.16f, %.16f" % (loc[0], loc[1])]
    else:
        return []

def resource_search(request):
    def _resource_result(r):
        result = {
            'id': r['res_id'],
            'title': r['title'],
            'description': r.get('short_description', ''),
            # 'resource_type': r[''] resource_type or '',
            'uri': r.get('uri', ''),
            'locations': r.get('pt_location', []),
            'locationnames': r.get('loc_labels', []),
            # u'loc_labels': [u'EH17 8QG, Liberton/Gilmerton, of Edinburgh'], u'pt_location': [u'55.9062925785, -3.13446285433']
            'tags': r.get('keywords', ''),
            'accounts': r.get('accounts', ''),
            'score': r['score']
            # 'last_modified': r[''] .item_metadata.last_modified,
        }
        if r.get('event_start'):
            result['event_start'] = r.get('event_start')
        if r.get('event_end'):
            result['event_end'] = r.get('event_end')
        return result

    location = request.REQUEST.get('location', '')
    accounts = request.REQUEST.get('accounts', '')
    collections = request.REQUEST.get('collections', '')
    if collections:
        accounts = ''
    event = request.REQUEST.get('event', None)
    query = request.REQUEST.get('query')
    max = request.REQUEST.get('max', unicode(settings.SOLR_ROWS))
    start = request.REQUEST.get('start', 0)
    output = request.REQUEST.get('output', 'json')
    boost_location = request.REQUEST.get('boostlocation', (settings.SOLR_LOC_BOOST_DEFAULT))
    callback = request.REQUEST.get('callback')

    increment_api_queries(query)
    increment_api_locations(location)

    result_code = 200

    errors = []
    # if not query:
    #     result_code = 10
    #     errors.append('Param \'query\' must be valid search query')
    if not _check_int(max) or int(max) > settings.SOLR_ROWS:
        result_code = 10
        errors.append('Param \'max\' must be positive integer maximum value of %s. You sent %s' % (settings.SOLR_ROWS, max))
    if not _check_int(start) or int(start) < 0:
        result_code = 10
        errors.append('Param \'start\' must be positive integer. You sent %s' % start)
    if not _check_int(boost_location) or int(boost_location) > int(settings.SOLR_LOC_BOOST_MAX):
        result_code = 10
        errors.append('Param \'boostlocation\' must be an integer number between 0 and %s. You sent %s' % (int(settings.SOLR_LOC_BOOST_MAX), boost_location))
    if event and event != '*':
        result_code = 10
        errors.append('Param \'event\' must be * if present.')
    if not errors:
        loc, resources = find_by_place_or_kwords(
            location, 
            query, 
            boost_location, 
            start=start, 
            max=int(max), 
            accounts=accounts.split(), 
            collections=collections.split(), 
            event=event)
        if location and not loc:
            result_code = 10
            errors.append('Location \'%s\' not found.' % location)

    if errors:
        return JsonResponse(errors=[{ 'code': result_code, 'message': '. '.join(errors)}], callback=callback)
    else:
        results = [_resource_result(r) for r in resources]
        data = [ { 'query': query, 'max': max, 'start': start, 'numfound': resources.hits, 'output': output,
            'location': _loc_to_str(loc), 'event': event, 'boostlocation': boost_location,
            'accounts': accounts, 'collections': collections,
            'results': results } ]
        return JsonResponse(data=data, callback=callback)


def publish_data(request):
    """docstring for publish_data"""
    def _resource_result(r):
        return {
            'id': unicode(r.id),
            'title': r.title,
            'description': r.description,
            'resource_type': r.resource_type,
            'uri': 'http://aliss.org/depot/resource/%s/' % unicode(r.id),
            'source_uri': r.uri,
            'locations': [{
                'postcode': l.postcode, 
                'place_name': l.place_name, 
                'loc_type': l.loc_type, 
                'lat_lon': l.lat_lon,
                'district': l.district,
                'country_code': l.country_code
                } for l in r.locations],
            # 'event_start': r.event_start,
            'tags': r.all_tags,
            'curations': ['http://aliss.org/depot/curation/%s/' % unicode(c.id) for c in r.curations],
            # 'accounts': r.get('accounts', ''),
            # 'score': r['score']
            # # 'last_modified': r[''] .item_metadata.last_modified,
        }

    max = request.REQUEST.get('max', unicode(settings.SOLR_ROWS))
    start = request.REQUEST.get('start', 0)
    callback = request.REQUEST.get('callback')

    result_code = 200

    errors = []
    if not _check_int(max) or int(max) > settings.SOLR_ROWS:
        result_code = 10
        errors.append('Param \'max\' must be positive integer maximum value of %s. You sent %s' % (settings.SOLR_ROWS, max))
    if not _check_int(start) or int(start) < 0:
        result_code = 10
        errors.append('Param \'start\' must be positive integer. You sent %s' % start)
    if errors:
        return JsonResponse(errors={ 'code': result_code, 'message': '. '.join(errors)}, data=[],  callback=callback)
        # return JsonResponse(data=[],  callback=callback)
    else:
        results = [_resource_result(r) for r in Resource.objects[int(start):int(start)+int(max)]]
        data = [ { 'max': max, 'start': start, 'results': results }]
        return JsonResponse(data=data, callback=callback)

def tags(request):
    """
        API call with optional params for callback and match
        callback: for jsonp callback function name
        match: if present, results will be alpha sorted list of all tags used starting with match
            (case insensitive, so "men" might return "mental health, Mental Health, mentoring")
            if match is not passed, all tags in use will be returned.
        returns alpha sorted list of strings
    """
    errors = []
    data = None
    result_code = 200

    # /api/tags/?callback=jsonp1268179474512&match=exe

    match = request.REQUEST.get('match')
    callback = request.REQUEST.get('callback')

    if not match is None:
        if len(match) > 2:
            results = [t for t in
                Curation.objects.ensure_index("tags").filter(tags__istartswith=match).distinct("tags") \
                    if t.lower().startswith(match.lower())]
        else:
            result_code = 10
            errors.append('Param \'match\' must be greater than 2 characters. You sent \'%s\'' % match)
    else:
        results = Curation.objects.ensure_index("tags").distinct("tags")

    if errors:
        return JsonResponse(errors={ 'code': result_code, 'message': '. '.join(errors)}, data=[],  callback=callback)

    return JsonResponse(data=sorted(results), callback=callback)

def locations(request):
    def _location_context(loc):
        return {
            'id': str(loc['_id']),
            'place_name': loc['place_name'],
            'postcode': loc.get('postcode', ''),
            'district': loc.get('district', '')}
    errors = []
    data = []
    response_code = 200

    match = request.REQUEST.get('match')
    callback = request.REQUEST.get('callback')

    if match and len(match) > 2:
        data = [_location_context(l)
            for l in get_location(match, just_one=False, starts_with=True)]
    else:
        response_code = 10
        errors.append('Param \'match\' must be greater than 2 characters. You sent \'%s\'' % match)
    return JsonResponse(
        errors=errors and {'code': response_code, 'message': '. '.join(errors)} or {},
        data=data,
        callback=callback,
    )

def savedsearchesbyIP(request):

    from accounts.models import AccountIPRange, SavedSearch, dqn_to_int

    callback = request.REQUEST.get('callback')
    ip = request.META['REMOTE_ADDR']

    int_ip = dqn_to_int(ip)

    data = []
    errors = {}

    try:
        account = AccountIPRange.objects.get(ip_min__lt=int_ip, ip_max__gt=int_ip)
        searches = SavedSearch.objects.get(owner=account.owner)
        data = searches.terms
    except AccountIPRange.DoesNotExist:
        errors = {
            'code': 404,
            'message': 'No account was found for the given IP range.'
        }
    except SavedSearch.DoesNotExist:
        errors = {
            'code': 404,
            'message': 'No saved searches were found for the account %s' % account.owner
        }

    return JsonResponse(
        errors=errors,
        data=data,
        callback=callback,
    )
