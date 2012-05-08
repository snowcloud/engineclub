from django import template

from accounts.models import get_account

register = template.Library()

@register.filter
def can_add(user, obj):
    """ usage {{ user|can_add:object }}"""
    return user.has_perm('can_add', obj)

@register.filter
def can_edit(user, obj):
    """ usage {{ user|can_edit:object }}"""
    return user.has_perm('can_edit', obj)

@register.filter
def can_delete(user, obj):
    """ usage {{ user|can_delete:object }}"""
    return user.has_perm('can_delete', obj)

@register.filter
def account(user):
	return get_account(user.id)

@register.filter
def account_id(user):
	acct = get_account(user.id)
	return acct.id if acct else ''

