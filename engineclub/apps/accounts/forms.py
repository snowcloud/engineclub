from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User

from ecutils.forms import DocumentForm
from models import Account


class AccountForm(DocumentForm):
    # class Meta:
    #     document = Account
    #     fields = ('name', 'email', 'description', 'local_id')

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)

class NewAccountForm(DocumentForm):
    class Meta:
        document = Account
        fields = ('name', 'email', 'description', 'local_id')
    
    description = forms.CharField(widget=forms.Textarea, required=False)
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Password (again)')
    local_id = forms.CharField(widget=forms.HiddenInput, required=False)

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
