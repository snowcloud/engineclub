
from django import forms

from depot.models import Item, get_nearest
from ecutils.forms import CSVTextInput
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
            p = geomaker(doc)
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

class FindItemForm(forms.Form):
    
    post_code = forms.CharField(help_text='enter a post code or a place name')
    tags = forms.CharField(widget=CSVTextInput, help_text='comma separated tags (spaces OK)', required=False)

    def __init__(self, *args, **kwargs):
        self.locations = []
        super(FindItemForm, self).__init__(*args, **kwargs)

    def clean_post_code(self):
        data = self.cleaned_data['post_code']
        places = fix_places(None, doc=data)
        if places:
            place = places[0]
            self.locations = get_nearest(place.centroid.latitude,place.centroid.longitude)
        else:
            raise forms.ValidationError("Could not find a location from what you've typed- try again?")
        return data

    def clean_tags(self):
        data = self.cleaned_data['tags']
        return [t.strip() for t in data.split(',')]
    
class ShortItemForm(DocumentForm):

    url = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)

    def clean_url(self):
        data = self.cleaned_data['url']
        try:
            item =Item.objects.get(url=data)
            if not (self.instance and (self.instance.url == data)):
                raise forms.ValidationError("There is already an item with this url")
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
        data = self.cleaned_data['tags']
        return [t.strip() for t in data.split(',')]
    
class ShelflifeForm(DocumentForm):
    """docstring for ShelflifeForm"""
    # dummy = forms.CharField(required=False)
    pass
           