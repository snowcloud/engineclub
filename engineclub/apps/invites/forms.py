from django import forms
from django.contrib.auth.models import User

from accounts.models import Account
from ecutils.forms import PlainForm
from invites.models import Invitation

class InvitationForm(PlainForm):

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-text large'}))

    def clean_email(self):

        if 'email' in self.cleaned_data:

            addr = self.data['email'].strip()
            accounts = Account.objects(email=addr).count()

            if accounts > 0:
                raise forms.ValidationError("'%s' already has an account." % addr)

            exists = Invitation.objects(email=addr).count()

            if exists > 0:
                raise forms.ValidationError("'%s' has already been invited." % addr)

        # mongo stores stripped string anyway :)
        return self.cleaned_data['email']


class InvitationAcceptForm(PlainForm):

    username = forms.RegexField(
        widget=forms.TextInput(attrs={'class': 'input-text large'}),
        regex=r'^\w+$',
        max_length=30,
        label='User name',
        help_text='You\'ll use this to log in- keep it short, with no spaces. Other people will not see this.' )
    accountname = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text expand'}),
        label='Full name',
        help_text='Please give the full name for your account, eg the full name of you or your organisation. You can change this later.')
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input-text large', 'maxlength': '75'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-text large'},),
        label='Password',
        help_text='Please make your password at least 6 characters long.'
        )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-text large'}),
        label='Password (repeated)',
        help_text='Please make this identical to the password above.')

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

    def clean_password1(self):
        pw = self.cleaned_data['password1']
        if len(pw) < 6:
            raise forms.ValidationError('Please make your password at least 6 characters long')
        return pw

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError('You must type the same password each time')
        return self.cleaned_data

    def save(self, profile_callback=None):

        username = self.cleaned_data['username']
        accountname = self.cleaned_data['accountname']

        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        new_user = User.objects.create_user(username, email, password)

        account = Account.objects.create(name=accountname, local_id=str(new_user.id),
            email=email,)

        return new_user, account
