from engine_groups.models import get_account

from notifications.models import Notification


def notifications(request):

    account = get_account(request.user.id)

    notifications = Notification.objects.for_account(account)
    notifications_count = len(notifications)

    return {
        'notifications_count': notifications_count,
        'notifications': notifications
    }
