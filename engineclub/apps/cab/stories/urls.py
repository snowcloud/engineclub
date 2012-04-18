# stories/urls.py

from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('stories.views',
    url(r'^$', 'stories_list', name="stories_list"),
    url(r'^(?P<object_id>[0-9A-Za-z]+)/$', 'stories_detail', name="stories_detail"),
)

