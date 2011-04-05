from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'enginecab.views.index', name='cab'),
    url(r'^reindex$', 'enginecab.views.reindex', name='cab-reindex'),
    

)
