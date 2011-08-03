
from django import forms

from depot.models import Resource, Curation, Location, find_by_place_or_kwords, get_place_for_placename
from ecutils.forms import CSVTextInput, clean_csvtextinput
from firebox.views import *

from mongoengine.queryset import DoesNotExist
from mongoforms import MongoForm


class FormHasNoInstanceException(Exception):
    pass

class DocumentForm(forms.Form):
    """docstring for DocumentForm"""

    instance = None

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            self.instance = instance
            kwargs.setdefault('initial', {}).update(instance.to_mongo())
        super(DocumentForm, self).__init__(*args, **kwargs)

    def save(self, do_save=False):
        if self.instance is None:
            raise FormHasNoInstanceException("Form cannot save- document instance is None.")
        for f in self.fields:
            self.instance[f] = self.cleaned_data[f]
        if do_save:
            self.instance.save()
        return self.instance

class FindResourceForm(forms.Form):
    
    post_code = forms.CharField(label='Location', help_text='enter a post code or a place name', required=False)
    tags = forms.CharField(widget=CSVTextInput, label='Search text:', help_text='comma separated text (spaces OK)', required=True)
    boost_location = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        self.locations = []
        self.results = []
        self.centre = None
        super(FindResourceForm, self).__init__(*args, **kwargs)

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
        kwords = cleaned_data.get('tags', '').strip()
        boost_location = cleaned_data.get('boost_location', '') or settings.SOLR_LOC_BOOST_DEFAULT
        
        if not(data or kwords):
            raise forms.ValidationError("Please enter a location and/or some text and try again.")

        loc, self.results = find_by_place_or_kwords(data, kwords, boost_location)
        if loc:
            self.centre = {'name': data, 'location': loc }
        elif data:
            raise forms.ValidationError("Could not find a location from what you've typed- try again?")
        # else:
        #     self.centre['location'] = get_place_for_placename('perth')['lat_lon'] #.split(settings.LATLON_SEP)
            
        return cleaned_data

class ShortResourceForm(DocumentForm):

    uri = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    # event = forms.DateTimeField(required=False)
    tags = forms.CharField(widget=CSVTextInput, label='Tags (keywords)', help_text='separate words or phrases with commas', required=False)

    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])

    def clean_uri(self):
        data = self.cleaned_data['uri']
        try:
            item =Resource.objects.get(uri=data)
            if not (self.instance and (self.instance.uri == data)):
                raise forms.ValidationError("There is already an item with this uri")
        except DoesNotExist:
            pass
        return data
    
class LocationUpdateForm(DocumentForm):
    
    new_location = forms.CharField(required=False)
    # address = forms.CharField(label="Location information", widget=forms.Textarea, required=False)
    # tags = forms.CharField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super(LocationUpdateForm, self).__init__(*args, **kwargs)
    #     if self.instance:
    #         for i, loc in enumerate(self.instance.locations):
    #             self.fields['itemloc_%s' % 1] = forms.BooleanField(label=loc.name, required=False)
    #     self.fields['address'] = forms.CharField(widget=forms.Textarea, required=False)
        
    
    # def content(self):
    #     # return '%s, %s' % (self.cleaned_data['postcode'], self.cleaned_data['address'])
    #     return self.cleaned_data['address']
    
class MetadataForm(DocumentForm):
    """docstring for MetadataForm"""
        
    last_modified = forms.DateField(required=False)
    shelflife = forms.CharField(required=False)
    author = forms.CharField(required=False)
    status = forms.CharField(required=False)
    admin_note = forms.CharField(widget=forms.Textarea, required=False)

class TagsForm(DocumentForm):
    """docstring for TagsForm"""
    tags = forms.CharField(widget=CSVTextInput, label='Tags (keywords)', help_text='separate words or phrases with commas', required=False)

    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])
    
class ShelflifeForm(DocumentForm):
    """docstring for ShelflifeForm"""
    # dummy = forms.CharField(required=False)
    pass
    
class CurationForm(DocumentForm):
    
    outcome = forms.CharField()
    tags = forms.CharField(widget=CSVTextInput, help_text='comma separated tags (spaces OK)', required=False)
    note = forms.CharField(widget=forms.Textarea, required=False)
    # data = forms.CharField(widget=forms.Textarea, required=False)
    
    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])

