
from django import forms

from apps.depot.models import Item


class ItemForm(forms.Form):
    
    name = forms.CharField(max_length=100)
    
    def clean_name(self):
        data = self.cleaned_data['name']
        if len(Item.objects(name=data)):
            raise forms.ValidationError("There is already an item with this name")

        return data
        