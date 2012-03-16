from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('issues.views',
    url(r'^$', 'issue_list', name="issue_list"),
    url(r'^(?P<object_id>[0-9A-Za-z]+)/$', 'issue_detail', name="issue_detail"),
)
