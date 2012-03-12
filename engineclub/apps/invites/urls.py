from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('invites.views',
    url(r'^$', 'index', name="invitations"),
    url(r'^add/$', 'invite', name="invite"),
    url(r'^(?P<code>\w+)/$', 'accept', name="invite-accept"),
    url(r'^(?P<object_id>\w+)/delete/$', 'remove', name='invite-delete'),

)
