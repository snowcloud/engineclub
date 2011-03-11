from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # Example:
    
    url(r'^resource/$', 'depot.views.resource_index', name='resource-list'),
    url(r'^resource/add/$', 'depot.views.resource_add', name='resource-add'),
    url(r'^resource/edit/(?P<object_id>\w+)/$', 'depot.views.resource_edit', name='resource-edit'),
    url(r'^resource/find/$', 'depot.views.resource_find', name='resource-find'),
    url(r'^resource/remove/(?P<object_id>\w+)/$', 'depot.views.resource_remove', name='resource-remove'),
    url(r'^resource/popup-cancel/$', direct_to_template, {'template': 'depot/resource_popup_cancel.html'}, name='resource-popup-cancel' ),
    url(r'^resource/popup-close/$', direct_to_template, {'template': 'depot/resource_popup_done.html'}, name='resource-popup-close' ),
    url(r'^resource/(?P<object_id>\w+)/$', 'depot.views.resource_detail', name='resource'),

)
