from django.conf.urls.defaults import *

urlpatterns = patterns('resources.api_handlers',
    url(r'^resources/search/$', 'resource_search', name='api_resource_search'),
    url(r'^resources/publishdata/$', 'publish_data', name='api_publish_data'),
    url(r'^resources/(?P<id>[^/]+)/$', 'resource_by_id', name='api_resource_by_id'),

    url(r'^savedsearchesbyIP/$', 'savedsearchesbyIP', name='savedsearchesbyIP'),

    url(r'^tags/$', 'tags'),
    url(r'^locations/$', 'locations'),

    # url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource),
)
