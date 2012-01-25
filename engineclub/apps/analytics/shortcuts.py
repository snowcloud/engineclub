from analytics.models import AccountAnalytics


def increment_tag(tag_name, account=None):
    AccountAnalytics(account).increment_tag(tag_name)


def increment_search(query, account=None):
    AccountAnalytics(account).increment_search(query)


def increment_location(location, account=None):
    AccountAnalytics(account).increment_location(location)
