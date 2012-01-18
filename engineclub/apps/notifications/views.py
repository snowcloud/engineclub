from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from engine_groups.models import get_account
from notifications.models import Notification


@login_required
def notifications_list(request):

    account = get_account(request.user.id)

    notifications = Notification.objects.for_account(account)

    return render_to_response('notifications/notifications_list.html', {
        'account': account,
        'notifications': notifications,
    }, RequestContext(request))
