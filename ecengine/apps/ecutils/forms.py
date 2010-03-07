from django import forms

# requires django-contact-form
from contact_form.views import contact_form
from contact_form.forms import ContactForm
from django.conf import settings

def clean_csvtextinput(data):
    """docstring for _clean_tags"""
    return [t.strip() for t in data.split(',')]

class CSVTextInput(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = ', '.join(value)
        return super(CSVTextInput, self).render(name, value, attrs)

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
    
