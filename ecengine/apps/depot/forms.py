
from django import forms

from depot.models import Item
from mongoengine.queryset import DoesNotExist

class FormHasNoInstanceException(Exception):
    pass
    
class ShortItemForm(forms.Form):
    
    url = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    instance = None
    
    def clean_url(self):
        data = self.cleaned_data['url']
        try:
            item =Item.objects.get(url=data)
            if not (self.instance and (self.instance.url == data)):
                raise forms.ValidationError("There is already an item with this url")
        except DoesNotExist:
            pass
        return data
    
    def save(self, do_save=True):
        if self.instance is None:
            raise FormHasNoInstanceException("Form cannot save- document instance is None.")
        # TODO update fields dynamically
        # for field in self.instance:
        #     print field
        # for field in self.fields:
        #     print field
        for f in self.fields:
            self.instance[f] = self.cleaned_data[f]
            
        if do_save:
            self.instance.save()
        return self.instance

class ItemForm(ShortItemForm):
    
    postcode = forms.CharField(required=False)
    area = forms.CharField(required=False)
    tags = forms.CharField(required=False)
    
class MetadataForm(forms.Form):
    """docstring for MetadataForm"""
        
    last_modified = forms.DateField(required=False)
    shelflife = forms.CharField(required=False)
    author = forms.CharField(required=False)
    status = forms.CharField(required=False)
    admin_note = forms.CharField(widget=forms.Textarea, required=False)
    