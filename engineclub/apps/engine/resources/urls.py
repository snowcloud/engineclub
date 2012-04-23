from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    # Example:

    url(r'^resource/$', 'resources.views.resource_index', name='resource_list'),
    url(r'^resource/add/', 'resources.views.resource_add', name='resource_add'),
    # url(r'^resource/add/(?P<path>\w+)/$', 'resources.views.resource_add', name='resource_add'),
    url(r'^resource/(?P<object_id>\w+)/edit/$', 'resources.views.resource_edit', name='resource_edit'),
    url(r'^resource/find/$', 'resources.views.resource_find', name='resource_find'),
    url(r'^resource/(?P<object_id>\w+)/remove/$', 'resources.views.resource_remove', name='resource_remove'),
    url(r'^resource/popup_cancel/$', TemplateView.as_view(template_name='depot/resource_popup_cancel.html'), name='resource_popup_cancel' ),
    url(r'^resource/popup_close/$', TemplateView.as_view(template_name='depot/resource_popup_done.html'), name='resource_popup_close' ),
    url(r'^resource/(?P<object_id>\w+)/$', 'resources.views.resource_detail', name='resource'),
    url(r'^resource/(?P<object_id>\w+)/report/$', 'resources.views.resource_report', name='resource_report'),

    url(r'^curation/(?P<object_id>\w+)/$', 'resources.views.curation_detail', name='curation_by_id'),
    url(r'^curation/(?P<object_id>\w+)/add/$', 'resources.views.curation_add', name='curation_add'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/$', 'resources.views.curation_detail', name='curation'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/edit/$', 'resources.views.curation_edit', name='curation_edit'),
    url(r'^curation/(?P<object_id>\w+)/(?P<index>\w+)/remove/$', 'resources.views.curation_remove', name='curation_remove'),

    url(r'^group/(?P<object_id>\w+)/curations/$', 'resources.views.curations_for_group', name='curations_for_group'),
    url(r'^group/(?P<object_id>\w+)/curations.html$', 'resources.views.curations_for_group_html', name='curations_for_group_html'),
    url(r'^group/(?P<object_id>\w+)/curations.js$', 'resources.views.curations_for_group_js', name='curations_for_group_js'),

    url(r'^location/(?P<object_id>\w+)/(?P<index>\w+)/remove/$', 'resources.views.location_remove', name='location_remove'),

)
