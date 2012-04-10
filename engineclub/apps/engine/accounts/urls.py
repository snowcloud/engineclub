from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    
    url(r'^$', 'accounts.views.index', name='accounts'),
    # url(r'^new/$', 'accounts.views.new', name='group-new'),
    url(r'^(?P<object_id>\w+)/$', 'accounts.views.detail', name='account_detail'),
    # url(r'^(?P<object_id>\w+)/edit/$', 'accounts.views.edit', name='group-edit'),

    )