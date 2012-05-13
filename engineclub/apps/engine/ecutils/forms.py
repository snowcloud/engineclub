from django import forms
from django.forms.forms import BoundField
from django.forms.widgets import CheckboxInput
from django.utils.html import conditional_escape
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.safestring import mark_safe

# import floppyforms as floppyforms

# requires django-contact-form
from contact_form.views import contact_form
from contact_form.forms import ContactForm
from django.conf import settings

class PlainForm(forms.Form):
    """docstring for ClassName"""

    def __init__(self, *args, **kwargs):
        if 'label_suffix' not in kwargs:
            kwargs['label_suffix'] = ''
        super(PlainForm, self).__init__(*args, **kwargs)

    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row, checkbox_row=''):
        """
        Helper function for outputting HTML. Used by as_table(), as_ul(), as_p().
        modified for Engineclub to wrap checkbox in label for Foundation markup with label to right.
        Hopefully a temporary hack until Django sorts out its form handling.
        """
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            
            # MOD FOR ENGINECLUB
            checkbox = isinstance(field.widget, CheckboxInput)

            html_class_attr = ''
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                # Create a 'class="..."' atribute if the row should have any
                # CSS classes applied.
                css_classes = bf.css_classes()
                if css_classes:
                    html_class_attr = ' class="%s"' % css_classes

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix

                    # MOD FOR ENGINECLUB
                    if not checkbox:
                        label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''

                # MOD FOR ENGINECLUB
                output_row = checkbox_row if checkbox else normal_row

                output.append(output_row % {
                    'errors': force_unicode(bf_errors),
                    'label': force_unicode(label),
                    'field': unicode(bf),
                    'help_text': help_text,
                    'html_class_attr': html_class_attr
                })

        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))

        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {'errors': '', 'label': '',
                                              'field': '', 'help_text':'',
                                              'html_class_attr': html_class_attr})
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))

    def as_plain(self):
        "Returns this form rendered as HTML with no tags wrapping a field."
        return self._html_output(
            normal_row = u'%(label)s %(field)s %(errors)s %(help_text)s',
            checkbox_row = u'<label>%(field)s %(label)s</label>%(errors)s %(help_text)s',
            # normal_row = u'<span%(html_class_attr)s>%(label)s %(field)s%(help_text)s</span>',
            error_row = u'%s',
            row_ender = '</span>',
            help_text_html = u' <span class="helptext">%s</span>',
            # make this False to include errors in format strings above
            errors_on_separate_row = False)

def clean_csvtextinput(data):
    """docstring for _clean_tags"""
    return [t.strip() for t in data.split(',') if t]

def checktags(data, user):
    # data = self.cleaned_data['tags']
    if '#' in data and not (user and user.is_staff):
        raise forms.ValidationError('You cannot use the # character in your tags.')
    return clean_csvtextinput(data)

class CSVTextInput(forms.TextInput):
    """a widget that will display list of strings as CSV
        Use with clean_csvtextinput on formfield validation to convert CSV input to list
        NB: this would be better wrapped up in a custom FormField
        TODO: ...
    """
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = ', '.join(value)
        return super(CSVTextInput, self).render(name, value, attrs)

class DocumentForm(PlainForm):
    """docstring for DocumentForm"""

    instance = None

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            self.instance = instance
            kwargs.setdefault('initial', {}).update(instance.to_mongo())
        super(DocumentForm, self).__init__(*args, **kwargs)

    def is_valid(self, user=None):
        self.req_user = user
        return super(DocumentForm, self).is_valid()

    def save(self, do_save=True):
        if self.instance is None:
            raise FormHasNoInstanceException("Form cannot save- document instance is None.")
        for f in self.fields:
            try:
                if self.cleaned_data[f] or self.instance[f]:
                    self.instance[f] = self.cleaned_data[f]
            except KeyError:
                pass
        if do_save:
            self.instance.save()
        return self.instance


class SCContactForm(ContactForm):
    """simple spam prevention for contact form- reject message body with 'http:'
    All the spam I have through contact emails has links in it.
    """
    recipient_list = [mail_tuple[1] for mail_tuple in settings.CONTACT_EMAILS]

    def clean_body(self):
        data = self.cleaned_data['body']
        if data.find('http:') > -1:
            raise forms.ValidationError("Please remove any links in your message.")

        return data

class FileUploadForm(PlainForm):
    picture_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'input-text expand'}), help_text='Pic must be JPG, 500w x 400h')

class ConfirmForm(PlainForm):
    object_name = forms.CharField(label='Name', max_length=96,
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
