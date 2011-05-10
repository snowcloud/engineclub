from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'enginecab.views.index', name='cab'),
    url(r'^reindex/$', 'enginecab.views.reindex', name='cab-reindex'),
    url(r'^fix-resource-accounts/$', 'enginecab.views.fix_resource_accounts', name='cab-fix-resource-accounts'),
    url(r'^one-off-util/$', 'enginecab.views.one_off_util', name='cab-one-off-util'),
    url(r'^remove-dud-curations/$', 'enginecab.views.remove_dud_curations', name='remove-dud-curations'),
    url(r'^show-curationless-resources/$', 'enginecab.views.show_curationless_resources', name='show-curationless-resources'),
    url(r'^fix-curationless-resources/$', 'enginecab.views.fix_curationless_resources', name='fix-curationless-resources'),
    
)
