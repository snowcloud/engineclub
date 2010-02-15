from django.conf.urls.defaults import *


urlpatterns = patterns('',
    # Example:
    
    url(r'^item/$', 'apps.depot.views.item_index', name='item-list'),
    url(r'^item/add/$', 'apps.depot.views.item_add', name='item-add'),
    url(r'^item/edit/(?P<object_id>\w+)/$', 'apps.depot.views.item_edit', name='item-edit'),
    url(r'^item/remove/(?P<object_id>\w+)/$', 'apps.depot.views.item_remove', name='item-remove'),
    url(r'^item/(?P<object_id>\w+)/$', 'apps.depot.views.item_detail', name='item'),

)
