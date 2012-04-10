# issues/forms.py

from django import forms

from ecutils.forms import PlainForm
from issues.models import RESOLUTION_CHOICES

class IssueResolveForm(PlainForm):
    resolved = forms.ChoiceField(
        widget= forms.RadioSelect,
        choices=RESOLUTION_CHOICES,
        label="Resolve this issue")
    resolved_message = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text large'}))

class CommentForm(PlainForm):
	message = forms.CharField(label='Your comment', widget=forms.Textarea(attrs={'class': 'input-text large'}))
