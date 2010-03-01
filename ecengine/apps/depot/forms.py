
from django import forms

from depot.models import Item
from mongoengine.queryset import DoesNotExist

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
    
class ItemForm(ShortItemForm):
    
    postcode = forms.CharField(required=False)
    area = forms.CharField(required=False)
    tags = forms.CharField(required=False)
    
class MetadataForm(DocumentForm):
    """docstring for MetadataForm"""
        
    last_modified = forms.DateField(required=False)
    shelflife = forms.CharField(required=False)
    author = forms.CharField(required=False)
    status = forms.CharField(required=False)
    admin_note = forms.CharField(widget=forms.Textarea, required=False)
    