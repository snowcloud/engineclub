from accounts.models import get_account

from notifications.models import Notification


def notifications(request):

    account = get_account(request.user.id)

    if account:
        notifications = Notification.objects.for_account(account).filter(
            opened=False, resolved=False)
        notifications_count = len(notifications)
    else:
        notifications = None
        notifications_count = 0

    return {
        'notifications_count': notifications_count,
        'notifications': notifications
    }
