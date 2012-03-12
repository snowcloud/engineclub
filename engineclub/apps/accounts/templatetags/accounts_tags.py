from django import template

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


