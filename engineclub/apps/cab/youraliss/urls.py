from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'youraliss.views.profile', name='youraliss'),
    url(r'^account/$', 'youraliss.views.account', name='youraliss_account'),
    url(r'^curations/$', 'youraliss.views.curations', name='youraliss_curations'),
    url(r'^lists/$', 'youraliss.views.lists', name='youraliss_lists'),
    url(r'^lists/(?P<object_id>\w+)/$', 'youraliss.views.lists_detail', name='youraliss_lists_detail'),
    (r'^issues/', include('issues.urls')),
    url(r'^(?P<object_id>\w+)/$', 'youraliss.views.profile', name='youraliss'),

)
