from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('notifications.views',
    url(r'^$', 'notifications_list', name="notifications-list"),
    url(r'^(?P<notification_id>[0-9A-Za-z]+)/$', 'notification_detail', name="notifications-detail"),
)
