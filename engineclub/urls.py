from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from contact_form.views import contact_form
from ecutils.forms import SCContactForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    
    (r'^$', 'home.views.index'),
    (r'^api/', include('depot.api_urls')),
    (r'^cab/', include('enginecab.urls')),
    (r'^depot/', include('depot.urls')),

    url(r'^contact/$', contact_form, { 'form_class': SCContactForm }, name='contact_form'),
    url(r'^contact/sent/$', direct_to_template, { 'template': 'contact_form/contact_form_sent.html' },
        name='contact_form_sent'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.contrib.auth.views',
    (r'^logout/$', 'logout' ) ,
    (r'^accounts/login/', 'login' ),
    (r'^password_reset/$','password_reset' ),
    (r'^password_reset/done/$', 'password_reset_done' ),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
    (r'^reset/done/$', 'password_reset_complete'),
    (r'^accounts/password_change/$', 'password_change' ),
    (r'^accounts/password_change/done/$', 'password_change_done' ),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$',
      'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT}
    ),
  )
