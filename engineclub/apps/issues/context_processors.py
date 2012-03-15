from accounts.models import get_account

from issues.models import AccountMessage


def message_stats(request):

    account = get_account(request.user.id)

    if account:
        messages = AccountMessage.objects.filter(to_account=account)
        message_count = len(messages)
    else:
        messages = None
        message_count = 0

    return {
        'message_count': message_count,
        'messages': messages
    }
