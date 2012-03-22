
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet

from depot.models import Resource, Curation, Location, find_by_place_or_kwords
from ecutils.forms import DocumentForm, PlainForm, CSVTextInput, clean_csvtextinput
from firebox.views import *
from issues.models import SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL

from mongoengine.queryset import DoesNotExist

from datetime import datetime

class FormHasNoInstanceException(Exception):
    pass

class FindResourceForm(PlainForm):
    
    post_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), label='Location', help_text='enter a post code or a place name', required=False)
    kwords = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), label='Search text', help_text='comma separated text (spaces OK)', required=False)
    events_only = forms.BooleanField(required=False)
    boost_location = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.locations = []
        self.results = []
        self.centre = None
        if 'label_suffix' not in kwargs:
            kwargs['label_suffix'] = ''
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
        kwords = cleaned_data.get('kwords', '').strip()
        boost_location = cleaned_data.get('boost_location', '') or settings.SOLR_LOC_BOOST_DEFAULT
        event = cleaned_data.get('events_only')

        if not(data or kwords):
            raise forms.ValidationError("Please enter a location and/or some text and try again.")

        loc, self.results = find_by_place_or_kwords(data, kwords, boost_location, event='*' if event else None)
        if loc:
            self.centre = {'name': data, 'location': loc }
        elif data:
            raise forms.ValidationError("Could not find a location from what you've typed- try again?")
            
        return cleaned_data

class ShortResourceForm(DocumentForm):

    uri = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}),required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    tags = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), label='Tags (keywords)', help_text='separate words or phrases with commas', required=False)

    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])

    def clean_uri(self):
        data = self.cleaned_data['uri']
        if data:
            try:
                if self.instance:
                    # id__not=instance.id throws an error, this works
                    check = Resource.objects(id__not__in=[self.instance.id], uri=data)
                else:
                    check = Resource.objects(uri=data)
                if check.count() > 0:
                    raise forms.ValidationError("There is already an item with this uri")
            except DoesNotExist:
                pass
        return data
    
class EventForm(DocumentForm):
    
    from ecutils.fields import JqSplitDateTimeField
    from ecutils.widgets import JqSplitDateTimeWidget

    widget_attrs={'class': 'datetimepicker', 'date_class':'datepicker input-text','time_class':'timepicker input-text'}

    start = JqSplitDateTimeField(required=False,
        widget=JqSplitDateTimeWidget(attrs=widget_attrs.copy(), date_format='%d/%m/%Y'))
    end = JqSplitDateTimeField(required=False, 
        widget=JqSplitDateTimeWidget(attrs=widget_attrs, date_format='%d/%m/%Y'))

    def clean(self):
        start = self.cleaned_data.get('start', None)
        end = self.cleaned_data.get('end', None)
        now = datetime.now()
        if end:
            if start:
                if end < start:
                    raise forms.ValidationError('The start date must be earlier than the finish date.')
            else:
                raise forms.ValidationError('Please enter a start date.')
            if end < now:
                raise forms.ValidationError('The end date must be in the future.')
        elif start:
            if start < now:
                raise forms.ValidationError('The start date must be in the future.')

        return self.cleaned_data

class LocationUpdateForm(DocumentForm):
    # REPLACE
    new_location = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text expand'}), required=False)
    # new_location = forms.CharField(widget=CSVTextInput, required=False, help_text='comma separated text (spaces OK)')
    locations = None

    def clean_new_location(self):
        data = self.cleaned_data['new_location']
        loc_ids = data.split(',')
        locs = list(Location.objects(id__in=loc_ids))
        new_locs = [l for l in loc_ids if l not in [loc.id for loc in locs]]
        new_locs_errors = []
        for new_loc in new_locs:
            loc = Location.create_from(new_loc)
            if loc:
                locs.append(loc)
            else:
                new_locs_errors.append(new_loc)
        self.locations = locs
        if new_locs_errors:
            raise forms.ValidationError('Could not find these locations: %s' % ', '.join(new_locs_errors))
        return data

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
    
    outcome = forms.CharField(widget=forms.HiddenInput)

    tags = forms.CharField(widget=CSVTextInput(attrs={'class': 'input-text expand'}), help_text='comma separated tags (spaces OK)', required=False)
    note = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text expand'}), required=False)
    # data = forms.CharField(widget=forms.Textarea, required=False)
    
    def clean_tags(self):
        return clean_csvtextinput(self.cleaned_data['tags'])





class KeyValueForm(forms.Form):

    key = forms.CharField()
    value = forms.CharField(widget=forms.Textarea, required=False)


class BaseDictFormSet(BaseFormSet):

    def clean(self):

        """Checks that no pairs have the same key."""

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid
            # on its own
            return

        keys = []

        for form in self.forms:

            if len(keys) != 2:
                continue

            print form.cleaned_data
            cleaned = form.cleaned_data
            key = form.cleaned_data['key']

            if key in keys:
                raise forms.ValidationError("Two keys cannot have the same value.")

            keys.append(key)

        return super(BaseDictFormSet, self).clean()

    def save(self):

        return dict( (form.cleaned_data['key'], form.cleaned_data['value'])
                for form in self.forms if len(form.cleaned_data.keys()) == 2)




def dict_form_factory(initial, extra=0, **kwargs):

    print initial.keys()

    DictFormSet = formset_factory(KeyValueForm, extra=extra,
                                    formset=BaseDictFormSet)

    form_initial = [{'key': k, 'value': v} for k, v in initial.items()]

    return DictFormSet(initial=form_initial, **kwargs)

REPORT_CHOICES=(
    (SEVERITY_LOW, 'Not serious- a spelling mistake or some other small correction'), 
    (SEVERITY_MEDIUM, 'Quite serious- something wrong, misleading, or should be checked'), 
    (SEVERITY_HIGH, 'Serious- content that might not suitable for ALISS'),
    (SEVERITY_CRITICAL, 'Very serious- content that is dangerous or offensive')
    )

class ResourceReportForm(PlainForm):
    severity = forms.ChoiceField(
        widget= forms.RadioSelect,
        choices=REPORT_CHOICES,
        label="How serious is this?")
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-text large'}))
