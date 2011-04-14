from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'enginecab.views.index', name='cab'),
    url(r'^reindex$', 'enginecab.views.reindex', name='cab-reindex'),
    url(r'^fix-resource-accounts$', 'enginecab.views.fix_resource_accounts', name='cab-fix-resource-accounts'),
    url(r'^one-off-util$', 'enginecab.views.one_off_util', name='cab-one-off-util'),
    
)
