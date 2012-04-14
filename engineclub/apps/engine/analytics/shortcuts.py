from analytics.models import AccountAnalytics


def increment_tags(tag_name, account=None):
    return
    if not tag_name:
        return
    AccountAnalytics(account).increment_tags(tag_name)


def increment_queries(query, account=None):
    return
    if not query:
        return
    AccountAnalytics(account).increment_queries(query)


def increment_locations(location, account=None):
    return
    if not location:
        return
    AccountAnalytics(account).increment_locations(location)


def increment_api_queries(query, account=None):
    return
    if not query:
        return
    AccountAnalytics(account).increment_api_queries(query)


def increment_api_locations(location, account=None):
    return
    if not location:
        return
    AccountAnalytics(account).increment_api_locations(location)


def increment_resources(object_id, account=None):
    return
    if not object_id:
        return
    AccountAnalytics(account).increment_resources(object_id)


def increment_api_resources(object_id, account=None):
    return
    if not object_id:
        return
    AccountAnalytics(account).increment_api_resources(object_id)


def increment_resource_crud(action_type, account=None):
    return
    AccountAnalytics(account).increment_resource_crud(action_type)
