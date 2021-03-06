from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TextInput
from time import strftime

# from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

class JqSplitDateTimeWidget(MultiWidget):

    def __init__(self, attrs=None, date_format='%d/%m/%Y', time_format=None):
        date_class = attrs.pop('date_class', None)
        time_class = attrs.pop('time_class', None)
        self.main_class = attrs.pop('class', None)

        time_attrs = attrs.copy()
        time_attrs['class'] = time_class
        date_attrs = attrs.copy()
        date_attrs['class'] = date_class

        self.date_format = date_format
        widgets = (DateInput(attrs=date_attrs, format=date_format),
                   TextInput(attrs=time_attrs), TextInput(attrs=time_attrs),
                   Select(attrs=attrs, choices=[('AM','AM'),('PM','PM')]))

        super(JqSplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = strftime(self.date_format, value.timetuple())
            hour = strftime("%I", value.timetuple())
            minute = strftime("%M", value.timetuple())
            meridian = strftime("%p", value.timetuple())
            return (d, hour, minute, meridian)
        else:
            return (None, None, None, None)

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.

        Returns a Unicode string representing the HTML for the whole lot.
        """
        class_attr = u' class="%s"' % self.main_class if self.main_class else ''
        return u'<div%s><span class="sublabel">Date:</span> %s<br/><span class="sublabel">Time:</span> %s:%s %s</div>' % (
                class_attr,
                rendered_widgets[0],
                rendered_widgets[1],
                rendered_widgets[2],
                rendered_widgets[3])

    class Media:
        css = {
            }
        js = (
            "js/jqsplitdatetime.js",
            )
