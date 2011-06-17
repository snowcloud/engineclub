from django.conf.urls.defaults import *

urlpatterns = patterns('depot.api_handlers',
    url(r'^resources/search/$', 'resource_search', name='api-resource-search'), 
    url(r'^resources/(?P<id>[^/]+)/$', 'resource_by_id', name='api-resource-by-id'), 
    url(r'^tags/$', 'tags'), 


    # url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource), 
)
