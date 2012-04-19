from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.base import TemplateView

from contact_form.views import contact_form
from ecutils.forms import SCContactForm

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'home.views.index', name='index'),
    url(r'^home/$', 'home.views.home', name='home'),
    (r'^acct/', include('youraliss.urls')),
    (r'^api/', include('resources.api_urls')),
    (r'^cab/', include('enginecab.urls')),
    (r'^depot/', include('resources.urls')),
    (r'^users/', include('accounts.urls')),
    (r'^stories/', include('stories.urls')),
    url(r'^search/$', 'resources.views.resource_find', name='search'),

    url(r'^contact/$', contact_form, { 'form_class': SCContactForm }, name='contact'),
    url(r'^contact/sent/$', TemplateView.as_view(template_name='contact_form/contact_form_sent.html'),
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
    url(r'^accounts/password_change/$', 'password_change', name='password_change'),
    (r'^accounts/password_change/done/$', 'password_change_done' ),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$',
      'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT}
    ),
  )
