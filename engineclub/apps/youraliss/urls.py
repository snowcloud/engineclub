from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'youraliss.views.index', name='youraliss'),
    url(r'^account/$', 'youraliss.views.account', name='youraliss_account'),
    url(r'^curations/$', 'youraliss.views.curations', name='youraliss_curations'),
    url(r'^groups/$', 'youraliss.views.groups', name='youraliss_groups'),
    (r'^issues/', include('issues.urls')),

)
