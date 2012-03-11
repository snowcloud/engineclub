from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from contact_form.views import contact_form
from ecutils.forms import SCContactForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'home.views.index', name='home'),
    (r'^api/', include('depot.api_urls')),
    (r'^cab/', include('enginecab.urls')),
    (r'^depot/', include('depot.urls')),
    (r'^groups/', include('accounts.urls')),
    (r'^notifications/', include('notifications.urls')),
    url(r'^search/$', 'depot.views.resource_find', name='search'),
    (r'^youraliss/', include('youraliss.urls')),


    url(r'^contact/$', contact_form, { 'form_class': SCContactForm }, name='contact'),
    url(r'^contact/sent/$', direct_to_template, { 'template': 'contact_form/contact_form_sent.html' },
        name='contact_form_sent'),

    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', name='logout') ,
    url(r'^accounts/login/', 'login', name='login'),
    url(r'^password_reset/$','password_reset', name='password_reset'),
    (r'^password_reset/done/$', 'password_reset_done' ),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
    (r'^reset/done/$', 'password_reset_complete'),
    (r'^accounts/password_change/$', 'password_change' ),
    (r'^accounts/password_change/done/$', 'password_change_done' ),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$',
      'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT}
    ),
  )
