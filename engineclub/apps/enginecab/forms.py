# enginecab/forms.py

from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User

from ecutils.forms import DocumentForm
from models import Account


class AccountForm(DocumentForm):

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
