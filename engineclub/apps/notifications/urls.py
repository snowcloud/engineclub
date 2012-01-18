from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('notifications.views',
    url(r'^$', 'notifications_list', name="notifications-list"),
)
