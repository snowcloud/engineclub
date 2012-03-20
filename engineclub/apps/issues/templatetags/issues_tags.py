# issues_tags.py

from django.template import Library, Node, Variable
from django.utils.safestring import mark_safe

from issues.models import SEVERITY_CHOICES, RESOLUTION_CHOICES

SEVERITY_LABEL_CLASSES = ['white', 'blue', 'black', 'red']

# SEVERITY_CHOICES = (
#     (SEVERITY_LOW, 'Low'),
#     (SEVERITY_MEDIUM, 'Medium'),
#     (SEVERITY_HIGH, 'High'),
#     (SEVERITY_CRITICAL, 'Critical'),
# )

register = Library()

@register.filter
def issue_severity(value, labels=None):
	return SEVERITY_CHOICES[value][1]

@register.filter
def can_resolve(account, issue):
	resolvers = [issue.reporter] + [issue.related_document.owner]
	return account.is_staff or account in resolvers

@register.filter
def display_resolved(value):
	for res in RESOLUTION_CHOICES:
		if res[0] == value:
			return res[1]
	return ''