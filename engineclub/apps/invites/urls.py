from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('invites.views',
    url(r'^$', 'invite', name="invite"),
    url(r'^(?P<code>\w+)/$', 'accept', name="invite_accept"),
)
