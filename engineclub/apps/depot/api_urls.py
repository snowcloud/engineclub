from django.conf.urls.defaults import *

urlpatterns = patterns('depot.api_handlers',
	url(r'^items/(?P<id>[^/]+)/$', 'item_resource'), 
	url(r'^tags/$', 'tags'), 


    # url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource), 
)
