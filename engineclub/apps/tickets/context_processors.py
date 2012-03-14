from accounts.models import get_account

from tickets.models import Alert


def alert_stats(request):

    account = get_account(request.user.id)

    if account:
        alerts = Alert.objects.for_account(account).filter(
            opened=False, resolved=False)
        alerts_count = len(alerts)
    else:
        alerts = None
        alerts_count = 0

    return {
        'alerts_count': alerts_count,
        'alerts': alerts
    }
