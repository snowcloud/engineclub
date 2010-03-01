from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    # Example:
    
    url(r'^item/$', 'depot.views.item_index', name='item-list'),
    url(r'^item/add/$', 'depot.views.item_add', name='item-add'),
    url(r'^item/edit/(?P<object_id>\w+)/$', 'depot.views.item_edit', name='item-edit'),
    url(r'^item/remove/(?P<object_id>\w+)/$', 'depot.views.item_remove', name='item-remove'),
    url(r'^item/popup-cancel/$', direct_to_template, {'template': 'depot/item_popup_cancel.html'}, name='item-popup-cancel' ),
    url(r'^item/popup-close/$', direct_to_template, {'template': 'depot/item_popup_done.html'}, name='item-popup-close' ),
    url(r'^item/(?P<object_id>\w+)/$', 'depot.views.item_detail', name='item'),

)
