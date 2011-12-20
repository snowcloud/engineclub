from analytics.models import AccountAnalytics


def increment_tag(account, tag_name):
    AccountAnalytics(account).increment_tag(tag_name)


def increment_search(account, query):
    AccountAnalytics(account).increment_search(query)
