from django.shortcuts import render_to_response
from django.template import RequestContext

from engine_groups.models import get_account


def notifications_list(request):

    user = get_account(request.user.id)

    return render_to_response('notifications/notifications_list.html', {
        'user': user,
    }, RequestContext(request))
