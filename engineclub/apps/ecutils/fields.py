


# from time import strptime, strftime
from datetime import datetime
from django import forms
from django.db import models
from django.forms import fields
from ecutils.widgets import JqSplitDateTimeWidget

# from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/
# modified D Hoy to improve validation

class JqSplitDateTimeField(fields.MultiValueField):
    widget = JqSplitDateTimeWidget

    def __init__(self, *args, **kwargs):
        """
        Have to pass a list of field types to the constructor, else we
        won't get any data to our compress method.
        """
        all_fields = (
            fields.CharField(max_length=10),
            fields.CharField(max_length=2),
            fields.CharField(max_length=2),
            fields.ChoiceField(choices=[('AM','AM'),('PM','PM')],initial='PM')
            )
        super(JqSplitDateTimeField, self).__init__(all_fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Takes the values from the MultiWidget and passes them as a
        list to this function. This function needs to compress the
        list into a single object to save.
        """
        if data_list:
            if data_list[0] or data_list[1] or data_list[2]:
                # added defaults so formatting doesn't fail
                # default to 12PM => midnight
                time1 = data_list[1] or '12'
                time2 = data_list[2] or '00'
                time3 = data_list[3] or 'PM'
                datetime_string = "%s %s:%s%s" % (data_list[0], time1, time2, time3)
                try:
                    return datetime.strptime(datetime_string, '%d/%m/%Y %I:%M%p')
                except ValueError:
                    raise forms.ValidationError("Please enter a valid date (time is optional)")
        return None
