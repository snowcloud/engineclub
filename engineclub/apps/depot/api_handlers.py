from django.conf import settings
from django.core import serializers 
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.http import HttpResponse

from depot.models import Resource, find_by_place_or_kwords

from mongoengine import ValidationError
from mongoengine.connection import _get_db as get_db

import re
from django.utils import simplejson as json

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

    data=[{
        'id': unicode(item.id),
        'title': item.title, 
        'description': item.description,
        'resourcetype': item.resource_type or '',
        'uri': item.uri,
        'locations': [loc.label for loc in item.locations],
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
        
def resource_search(request):
    def _resource_result(r):
        return {
            'id': r['res_id'],
            'title': r['title'], 
            'description': r['short_description'],
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
    location = request.REQUEST.get('location', '')
    accounts = request.REQUEST.get('accounts', '')
    query = request.REQUEST.get('query')
    max = request.REQUEST.get('max', unicode(settings.SOLR_ROWS))
    start = request.REQUEST.get('start', 0)
    output = request.REQUEST.get('output', 'json')
    boost_location = request.REQUEST.get('boostlocation', (settings.SOLR_LOC_BOOST_DEFAULT))
    callback = request.REQUEST.get('callback')

    # print accounts.split()
    
    result_code = 200
    
    errors = []
    if not query:
        result_code = 10
        errors.append('Param \'query\' must be valid search query')
    if not _check_int(max) or int(max) > settings.SOLR_ROWS:
        result_code = 10
        errors.append('Param \'max\' must be positive integer maximum value of %s. You sent %s' % (settings.SOLR_ROWS, max))
    if not _check_int(start) or int(start) < 0:
        result_code = 10
        errors.append('Param \'start\' must be positive integer. You sent %s' % start)
    if not _check_int(boost_location) or int(boost_location) > int(settings.SOLR_LOC_BOOST_MAX):
        result_code = 10
        errors.append('Param \'boostlocation\' must be an integer number between 0 and %s. You sent %s' % (int(settings.SOLR_LOC_BOOST_MAX), boost_location))
    if errors:
        return JsonResponse(errors={ 'code': result_code, 'message': '. '.join(errors)})
    else:
        kwords = query
        loc, resources = find_by_place_or_kwords(location, kwords, boost_location, start=start, max=int(max), accounts=accounts.split())

        results = [_resource_result(r) for r in resources]
        data = [ { 'query': query, 'max': max, 'start': start, 'output': output,
            'location': loc, 'boostlocation': boost_location,
            'results': results } ]
        return JsonResponse(data=data, callback=callback)
        

def publish_data(request):
    """docstring for publish_data"""
    def _resource_result(r):
        return {
            'id': unicode(r.id),
            'title': r.title, 
            'description': r.description[:120],
            'resource_type': r.resource_type,
            'uri': 'http://aliss.org/depot/resource/%s/' % unicode(r.id),
            'source_uri': r.uri,
            'locations': [{
                'os_id': l.os_id, 
                'label': l.label, 
                'place_name': l.place_name, 
                'os_type': l.os_type, 
                'lat_lon': l.lat_lon, 
                
                } for l in r.locations],
            'tags': r.tags,
            'curations': ['http://129.215.110.191:8080/depot/curation/%s/' % unicode(c.id) for c in r.curations],
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
        return JsonResponse(errors={ 'code': result_code, 'message': '. '.join(errors)})
    else:
        results = [_resource_result(r) for r in Resource.objects[int(start):int(start)+int(max)]]
        data = [ { 'max': max, 'start': start, 'results': results }]
        return JsonResponse(data=data, callback=callback)

def tags(request):
    """docstring for tags"""
    error = ''
    data = None
    
    # /api/api/tags/?callback=jsonp1268179474512&match=exe
    
    match = request.REQUEST.get('match')
    callback = request.REQUEST.get('callback')
    
    if match:
        db = get_db()
        update_keyword_index()
        results = db.keyword.find( { "_id" : re.compile('^%s*' % match, re.IGNORECASE)} ) #.count()
        data = [i['_id'] for i in results]
        # print data
    else:
        error = 'no match parameter received'
        
    if error:
        return JsonResponse(error=error)
    
    return JsonResponse(data=data, callback=callback)
        
    
    
    