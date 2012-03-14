from datetime import datetime

from django.core.mail import send_mail
from django.http import Http404
from django.template.loader import render_to_string
from mongoengine import *
from mongoengine.queryset import QuerySet
from mongoengine.base import ValidationError

from accounts.models import Account


class Ticket(Document):

    meta = {
        'allow_inheritance': False
    }



class AlertType(Document):

    meta = {
        'allow_inheritance': False
    }

    name = StringField()

    def __unicode__(self):
        return self.name


class AlertQuerySet(QuerySet):

    def create_for_accounts(self, accounts, **kwargs):
        """
        Create alerts for a list of accounts. This is done so that
        when a notification if given to a ticket of people, once one person
        deals with it, we can strike it off for all the others.
        """

        # For convenience allow type to be given as a string, and we will
        # automaticlally lookup/create the AlertType.
        if 'type' in kwargs and isinstance(kwargs['type'], basestring):
            kwargs['type'], _ = AlertType.objects.get_or_create(
                name=kwargs['type'])

        # If a ticket is provided (and its truthy), use that. Otherwise create
        # a new ticket if more than one account is going to be notified.
        if 'ticket' not in kwargs or not kwargs['ticket']:
            if len(accounts) > 1:
                kwargs['ticket'] = Ticket.objects.create()
            else:
                kwargs['ticket'] = None

        alerts = []
        for account in accounts:
            alerts.append(Alert.objects.create(
                account=account, **kwargs))
        return alerts

    def create_for_account(self, account, create_ticket=False, **kwargs):

        if create_ticket:
            kwargs['ticket'] = Ticket.objects.create()

        return self.create_for_accounts([account, ], **kwargs)[0]

    def for_account(self, account):
        """
        Wrapped into a simpler helper as we may want to change the behaviour
        later to retrieve alerts for sub or parent accounts based on
        the membership.
        """
        return self._user(account=account)

    def _user(self, account=None):
        # XXX: THIS MEANS A QUERY USING for_account WILL RETURN ALL NOTIFICATIONS IF NO ACCOUNT
        if account:
            return Alert.objects(account=account)
        else:
            return Alert.objects

    def low(self, user=None):
        return self._user(user)(severity=SEVERITY_LOW)

    def medium(self, user=None):
        return self._user(user)(severity=SEVERITY_MEDIUM)

    def high(self, user=None):
        return self._user(user)(severity=SEVERITY_HIGH)

    def critical(self, user=None):
        return self._user(user)(severity=SEVERITY_CRITICAL)

    def get_or_404(self, **kwargs):
        try:
            return self.get(**kwargs)
        except (Alert.DoesNotExist, ValidationError):
            raise Http404("Alert not found for %s" % kwargs)


SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL = (0, 1, 2, 3)

SEVERITY_CHOICES = (
    (SEVERITY_LOW, 'Low'),
    (SEVERITY_MEDIUM, 'Medium'),
    (SEVERITY_HIGH, 'High'),
    (SEVERITY_CRITICAL, 'Critical'),
)


class Alert(Document):

    meta = {
        'queryset_class': AlertQuerySet,
        'allow_inheritance': False
    }

    account = ReferenceField(Account, required=True)
    ticket = ReferenceField(Ticket, required=False)
    type = ReferenceField(AlertType, required=True)
    severity = IntField(choices=SEVERITY_CHOICES, required=True)
    datetime = DateTimeField(default=datetime.now)
    origin = ReferenceField(Account, required=False)
    message = StringField()
    opened = BooleanField(default=False)
    resolved = BooleanField(default=False)
    related_document = GenericReferenceField()

    def __unicode__(self):
        return self.message

    def mark_read(self):
        self.opened = True
        self.save()

    # def resolve(self):
    #     """
    #     If the alert is in a ticket, update the full notification
    #     ticket - including this one. Otherwise update only this notification.
    #     """

    #     if not self.ticket:
    #         self.resolved = True
    #         self.save()
    #         return

    #     for notification in Alert.objects(ticket=self.ticket):
    #         notification.resolved = True
    #         notification.save()

    def should_send_email(self):
        return True

    def send_email(self, request=None):

        alerts_count = Alert.objects.for_account(self.account
            ).filter(opened=False, resolved=False).count()

        message = render_to_string('tickets/alert_email.txt', {
            'account': self.account,
            'alerts_count': alerts_count
        })

        send_mail('ALISS Alerts', message, 'no-reply@aliss.org',
            [self.account.email], fail_silently=False)
