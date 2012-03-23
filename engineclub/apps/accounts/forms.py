from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User

from ecutils.forms import DocumentForm
from models import Account, EMAIL_UPDATE_CHOICES


class AccountForm(DocumentForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
    email_preference = forms.ChoiceField(choices=EMAIL_UPDATE_CHOICES, required=False)

class NewAccountForm(DocumentForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text expand'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text expand'}), label='Password (again)')
    local_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_url(self):
        # fix so that new Account can be filled with cleaned_data
        # without validation caused by empty string
        data = self.cleaned_data['url']
        return data or None

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get('email')
        local_id = cleaned_data.get('local_id')
        self.username = cleaned_data.get('username')
        self.password = cleaned_data.get('password')
        self.password2 = cleaned_data.get('password2')
        # subject = cleaned_data.get("subject")

        if local_id and self.username:
            raise forms.ValidationError("Please enter a local id or a username and passwords, but not both!")
        elif self.username:
            if self.password != self.password2:
                raise forms.ValidationError("Passwords are not the same.")
            try:
                user = User.objects.create_user(self.username, email, self.password)
                cleaned_data['local_id'] = str(user.id)
            except IntegrityError:
                raise forms.ValidationError("Could not create local user account- maybe username is taken?")
        return cleaned_data
