from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('analytics.views',
    url(r'^$', 'analytics_index', name="analytics"),
    url(r'^json/(?P<stat_name>[0-9_A-Za-z]+)/$', 'stat_json', name="analytics-json"),
    url(r'^stat/(?P<stat_name>[0-9_A-Za-z]+)/$', 'stat_view', name="analytics-stat"),
)
