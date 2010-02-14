
from django.forms import ModelForm

from apps.depot.models import TestItem


class ItemForm(ModelForm):
    class Meta:
        model = TestItem

