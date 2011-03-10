from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.core import serializers 

from depot.models import Resource, update_keyword_index

from mongoengine.connection import _get_db as get_db

import re
from django.utils import simplejson as json

class JsonResponse(HttpResponse):
    """from http://www.djangosnippets.org/snippets/1639/"""
    error = ""
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
                "error":self.error,
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
            
        if "error" in kwargs:
            self.error = kwargs.pop("error")
        
        if "callback" in kwargs:
            self.callback = kwargs.pop('callback')
            
        super(JsonResponse, self).__init__(*args, **kwargs)


def item_resource(request, id):
    """docstring for item_resource"""
    error = ''
    item = Resource.objects.get(id=id)
    # print item.title
    return JsonResponse(data=[item.title, unicode(item.id), item.description])
    
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
        
    
    
    