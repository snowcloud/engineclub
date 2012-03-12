from datetime import datetime
from hashlib import sha1
from random import random

from django.core.mail import send_mail
from django.template.loader import render_to_string
from mongoengine import *

from accounts.models import Account


class Invitation(Document):

    email = EmailField(required=True)
    code = StringField(max_length=40)
    invite_from = ReferenceField(Account, required=True)
    date_invited = DateTimeField(default=datetime.now, required=True)
    accepted = BooleanField(default=False, required=True)

    def __unicode__(self):
        return self.email

    def generate_code(self):

        salt = sha1(str(random())).hexdigest()[:5]
        code = sha1(salt + self.email).hexdigest()
        self.code = code

    def should_send_email(self):
        return True

    def send_email(self):

        from django.core.urlresolvers import reverse

        accept_url = reverse("invite-accept", args=[self.code, ])

        message = render_to_string('invites/invitation_email.txt', {
            'sender': self.invite_from,
            'accept_url': accept_url,
        })

        send_mail('ALISS Invitation', message, 'no-reply@aliss.org',
            [self.email], fail_silently=False)

    def save(self, *args, **kwargs):

        if not self.code:
            self.generate_code()

        super(Invitation, self).save(*args, **kwargs)
