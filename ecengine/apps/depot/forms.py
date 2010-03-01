
from django import forms

from depot.models import Item
from mongoengine.queryset import DoesNotExist


class ShortItemForm(forms.Form):
    
    url = forms.CharField()
    title = forms.CharField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    # postcode = forms.CharField(required=False)
    # area = forms.CharField(required=False)
    # tags = forms.CharField(required=False)
    # last_modified = forms.DateField(required=False)
    # shelflife = forms.CharField(required=False)
    author = forms.CharField(widget=forms.HiddenInput, required=False)
    # status = forms.CharField(required=False)
    # admin_note = forms.CharField(required=False)
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

class ItemForm(ShortItemForm):
    
    postcode = forms.CharField(required=False)
    area = forms.CharField(required=False)
    tags = forms.CharField(required=False)
    last_modified = forms.DateField(required=False)
    shelflife = forms.CharField(required=False)
    author = forms.CharField(required=False)
    status = forms.CharField(required=False)
    admin_note = forms.CharField(widget=forms.Textarea, required=False)
    