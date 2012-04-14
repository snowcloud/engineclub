from accounts.models import get_account

from issues.models import AccountMessage


def message_stats(request):

    account = get_account(request.user.id)

    if account:
        account_messages = AccountMessage.objects.filter(to_account=account)
        account_message_count = len(account_messages)
    else:
        account_messages = None
        account_message_count = 0

    return {
        'account_message_count': account_message_count,
        'account_messages': account_messages
    }
