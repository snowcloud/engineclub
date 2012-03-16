from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    # Example:

    url(r'^resource/$', 'depot.views.resource_index', name='resource-list'),
    url(r'^resource/add/$', 'depot.views.resource_add', name='resource-add'),
    url(r'^resource/(?P<object_id>\w+)/edit/$', 'depot.views.resource_edit', name='resource-edit'),
    url(r'^resource/find/$', 'depot.views.resource_find', name='resource-find'),
    url(r'^resource/(?P<object_id>\w+)/remove/$', 'depot.views.resource_remove', name='resource-remove'),
    url(r'^resource/popup-cancel/$', TemplateView.as_view(template_name='depot/resource_popup_cancel.html'), name='resource-popup-cancel' ),
    url(r'^resource/popup-close/$', TemplateView.as_view(template_name='depot/resource_popup_done.html'), name='resource-popup-close' ),
    url(r'^resource/(?P<object_id>\w+)/$', 'depot.views.resource_detail', name='resource'),
    url(r'^resource/(?P<object_id>\w+)/report/$', 'depot.views.resource_report', name='resource-report'),

    url(r'^curation/(?P<object_id>\w+)/$', 'depot.views.curation_detail', name='curation-by-id'),
    url(r'^curation/(?P<object_id>\w+)/add/$', 'depot.views.curation_add', name='curation-add'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/$', 'depot.views.curation_detail', name='curation'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/edit/$', 'depot.views.curation_edit', name='curation-edit'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/remove/$', 'depot.views.curation_remove', name='curation-remove'),
    url(r'^group/(?P<object_id>\w+)/curations/$', 'depot.views.curations_for_group', name='curations-for-group'),
    url(r'^group/(?P<object_id>\w+)/curations.html$', 'depot.views.curations_for_group_html', name='curations-for-group-html'),
    url(r'^group/(?P<object_id>\w+)/curations.js$', 'depot.views.curations_for_group_js', name='curations-for-group-js'),

    url(r'^location/(?P<object_id>\w+)/(?P<index>\w+)/remove/$', 'depot.views.location_remove', name='location-remove'),

)
