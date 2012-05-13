# enginecab/forms.py

from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User

from ecutils.forms import DocumentForm, PlainForm
from ecutils.models import Setting
from accounts.models import Account


class AccountForm(DocumentForm):

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)

UPPERCASE = 'tag_upper_case_exceptions'

class TagsFixerForm(PlainForm):
    def _get_bluff():
        setting, _ = Setting.objects.get_or_create(key=UPPERCASE)
        return '\n'.join(setting.value.get('data', []))

    split = forms.BooleanField(label='Split on commas/semicolons', required=False)
    lower_case = forms.BooleanField(label='Make lower case (apart from exceptions below)', required=False)
    upper_case_exceptions = forms.CharField(
        initial= _get_bluff,
        widget=forms.Textarea(attrs={'class': 'input-text expand'}),
        help_text='One tag per line- these will be saved.',
        required=False)

    def clean(self):
        # if errors in data, cleaned_data may be wiped, and/or fields not available
        cleaned_data = self.cleaned_data
        exceptions = cleaned_data['upper_case_exceptions']
        setting, _ = Setting.objects.get_or_create(pk=UPPERCASE)
        setting.value['data'] = [ex.strip() for ex in exceptions.split('\n') if ex.strip()]
        setting.save()
        self.exceptions = setting.value['data']
        return cleaned_data
