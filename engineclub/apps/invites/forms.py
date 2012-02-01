from django import forms
from django.contrib.auth.models import User

from engine_groups.models import Account


class InvitationForm(forms.Form):

    email = forms.EmailField()

    def clean_email(self):

        if 'email' in self.cleaned_data:

            accounts = Account.objects(email=self.data['email']).count()

            if accounts > 0:
                raise forms.ValidationError("This email address already has an account.")

        return self.cleaned_data['email']


class InvitationAcceptForm(forms.Form):

    username = forms.RegexField(regex=r'^\w+$', max_length=30)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)))
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('This username is already taken. Please choose another.')

    def clean_email(self):
        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('This email is already in use.')

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError('You must type the same password each time')
        return self.cleaned_data

    def save(self, profile_callback=None):

        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        new_user = User.objects.create_user(username, email, password)

        account = Account.objects.create(name=username, local_id=str(new_user.id),
            email=email,)

        return new_user, account
