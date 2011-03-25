
from django import forms

from depot.models import Resource, Location, find_by_place
from ecutils.forms import CSVTextInput, clean_csvtextinput
from firebox.views import *

from mongoengine.queryset import DoesNotExist


def fix_places(locations, doc=None):
    """docstring for fix_places"""
    result = []
    places = []
    itemlocs = []
    if locations:
        for loc in locations: #woeids
            itemlocs.append(loc)
            result.append(PlaceProxy(Location.objects.get(woeid=loc), checked=True))
    if doc:
        try:
            g = geomaker(doc)
            p = g.find_places()
            places= p.places
        except:
            places = []

    result.extend([place for place in places if unicode(place.woeid) not in itemlocs])  
    return result
    
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
    
    post_code = forms.CharField(help_text='enter a post code or a place name', required=True)
    tags = forms.CharField(widget=CSVTextInput, help_text='comma separated tags (spaces OK)', required=False)

    def __init__(self, *args, **kwargs):
        self.locations = []
        self.results = []
        self.centre = None
        super(FindResourceForm, self).__init__(*args, **kwargs)

    def clean(self):
        # if errors in data, cleaned_data may be wiped, and/or fields not available
        cleaned_data = self.cleaned_data
        data = cleaned_data.get('post_code').strip()
        kwords = cleaned_data.get('tags').strip()
        
        self.centre = {'name': data}
        loc, self.results = find_by_place(data, kwords)
        if loc:
            self.centre['location'] = loc #.split(settings.LATLON_SEP)
        else:
            raise forms.ValidationError("Could not find a location from what you've typed- try again?")
        
        return cleaned_data

class ShortResourceForm(DocumentForm):

    uri = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)

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
    
    # postcode = forms.CharField(required=False)
    address = forms.CharField(label="Location information", widget=forms.Textarea, required=False)
    # tags = forms.CharField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super(LocationUpdateForm, self).__init__(*args, **kwargs)
    #     if self.instance:
    #         for i, loc in enumerate(self.instance.locations):
    #             self.fields['itemloc_%s' % 1] = forms.BooleanField(label=loc.name, required=False)
    #     self.fields['address'] = forms.CharField(widget=forms.Textarea, required=False)
        
    
    def content(self):
        # return '%s, %s' % (self.cleaned_data['postcode'], self.cleaned_data['address'])
        return self.cleaned_data['address']
    
class MetadataForm(DocumentForm):
    """docstring for MetadataForm"""
        
    last_modified = forms.DateField(required=False)
    shelflife = forms.CharField(required=False)
    author = forms.CharField(required=False)
    status = forms.CharField(required=False)
    admin_note = forms.CharField(widget=forms.Textarea, required=False)

class TagsForm(DocumentForm):
    """docstring for TagsForm"""
    tags = forms.CharField(widget=CSVTextInput, help_text='comma separated tags (spaces OK)', required=False)

    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])
    
class ShelflifeForm(DocumentForm):
    """docstring for ShelflifeForm"""
    # dummy = forms.CharField(required=False)
    pass
           