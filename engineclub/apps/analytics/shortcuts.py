from analytics.models import AccountAnalytics


def increment_tag(tag_name, account=None):
    if not tag_name:
        return
    AccountAnalytics(account).increment_tag(tag_name)


def increment_search(query, account=None):
    if not query:
        return
    AccountAnalytics(account).increment_search(query)


def increment_location(location, account=None):
    if not location:
        return
    AccountAnalytics(account).increment_location(location)
