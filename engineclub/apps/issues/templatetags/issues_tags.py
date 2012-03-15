# issues_tags.py

from django.template import Library, Node, Variable
from django.utils.safestring import mark_safe

from issues.models import SEVERITY_CHOICES

SEVERITY_LABEL_CLASSES = ['white', 'blue', 'black', 'red']

# SEVERITY_CHOICES = (
#     (SEVERITY_LOW, 'Low'),
#     (SEVERITY_MEDIUM, 'Medium'),
#     (SEVERITY_HIGH, 'High'),
#     (SEVERITY_CRITICAL, 'Critical'),
# )

register = Library()

@register.filter
def alert_severity(value, labels=None):
	return SEVERITY_CHOICES[value][1]
