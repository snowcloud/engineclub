from django.conf.urls.defaults import *


urlpatterns = patterns('',
    
    url(r'^$', 'youraliss.views.index', name='youraliss'),
    url(r'^account/$', 'youraliss.views.account', name='youraliss-account'),
    url(r'^alerts/$', 'youraliss.views.alerts', name='youraliss-alerts'),
    url(r'^curations/$', 'youraliss.views.curations', name='youraliss-curations'),
    url(r'^groups/$', 'youraliss.views.groups', name='youraliss-groups'),
    (r'^issues/', include('issues.urls')),

)
