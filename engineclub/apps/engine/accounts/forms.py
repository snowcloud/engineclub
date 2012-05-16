from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError

from ecutils.forms import DocumentForm, PlainForm, CSVTextInput, checktags
from resources.search import find_by_place_or_kwords
from models import Account, EMAIL_UPDATE_CHOICES


class AccountForm(DocumentForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    tags = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), label='Tags (keywords)', help_text='separate words or phrases with commas', required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
    email_preference = forms.ChoiceField(choices=EMAIL_UPDATE_CHOICES, required=False)

    def clean_tags(self):
        return checktags(self.cleaned_data['tags'], self.req_user)


class NewAccountForm(DocumentForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    tags = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), label='Tags (keywords)', help_text='separate words or phrases with commas', required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text expand'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text expand'}), label='Password (again)')
    local_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_tags(self):
        return checktags(self.cleaned_data['tags'], self.req_user)


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

class FindAccountForm(PlainForm):
    
    post_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), label='Location', help_text='enter a post code or a place name', required=False)
    kwords = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), label='Search text', help_text='comma separated text (spaces OK)', required=False)
    # events_only = forms.BooleanField(required=False)
    boost_location = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.locations = []
        self.results = []
        self.centre = None
        if 'label_suffix' not in kwargs:
            kwargs['label_suffix'] = ''
        super(FindAccountForm, self).__init__(*args, **kwargs)

    def clean_boost_location(self):
        """docstring for clean_boost_location"""
        data = self.cleaned_data['boost_location']
        if data.isdigit():
            data = int(data)
            return data if data <= 100 else 100
        return ''

    def clean(self):
        # if errors in data, cleaned_data may be wiped, and/or fields not available
        cleaned_data = self.cleaned_data
        data = cleaned_data.get('post_code', '').strip()
        kwords = cleaned_data.get('kwords', '').strip()
        boost_location = cleaned_data.get('boost_location', '') or settings.SOLR_LOC_BOOST_DEFAULT
        # event = cleaned_data.get('events_only')

        if not(data or kwords):
            raise forms.ValidationError("Please enter a location and/or some text and try again.")

        loc, self.results = find_by_place_or_kwords(data, kwords, boost_location, res_type=settings.SOLR_ACCT)
        if loc:
            self.centre = {'name': data, 'location': loc['lat_lon'] }
        elif data:
            raise forms.ValidationError("Could not find a location from what you've typed- try again?")
            
        return cleaned_data

