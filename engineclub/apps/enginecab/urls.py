from django.conf.urls.defaults import *


urlpatterns = patterns('enginecab.views',
    
    url(r'^$', 'users', name='cab'),
    url(r'^alerts/$', 'alerts', name='cab-alerts'),
    url(r'^reindex/$', 'reindex', name='cab-reindex'),
    url(r'^resources/$', 'resources', name='cab-resources'),
    url(r'^users/$', 'users', name='cab-users'),
    url(r'^users/(?P<object_id>\w+)/$', 'user_detail', name='cab-user-detail'),
    url(r'^users/(?P<object_id>\w+)/edit/$', 'user_edit', name='cab-user-edit'),

    (r'^invite/', include('invites.urls')),

    # url(r'^fix-resource-accounts/$', 'enginecab.views.fix_resource_accounts', name='cab-fix-resource-accounts'),
    # url(r'^one-off-util/$', 'enginecab.views.one_off_util', name='cab-one-off-util'),
    # url(r'^remove-dud-curations/$', 'enginecab.views.remove_dud_curations', name='remove-dud-curations'),
    # url(r'^show-curationless-resources/$', 'enginecab.views.show_curationless_resources', name='show-curationless-resources'),
    # url(r'^fix-curationless-resources/$', 'enginecab.views.fix_curationless_resources', name='fix-curationless-resources'),
    
)
