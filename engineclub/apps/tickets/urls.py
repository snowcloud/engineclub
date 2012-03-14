from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('tickets.views',
    url(r'^$', 'alerts_list', name="alerts-list"),
    url(r'^(?P<alert_id>[0-9A-Za-z]+)/$', 'alert_detail', name="alert-detail"),
)
