from datetime import datetime

from django.core.mail import send_mail
from django.http import Http404
from django.template.loader import render_to_string
from mongoengine import *
from mongoengine.queryset import QuerySet
from mongoengine.base import ValidationError

from accounts.models import Account


class NotificationGroup(Document):
    pass


class NotificationType(Document):
    name = StringField()

    def __unicode__(self):
        return self.name


class NotificationQuerySet(QuerySet):

    def create_for_accounts(self, accounts, **kwargs):
        """
        Create notifications for a list of accounts. This is done so that
        when a notification if given to a group of people, once one person
        deals with it, we can strike it off for all the others.
        """

        # For convenience allow type to be given as a string, and we will
        # automaticlally lookup/create the NotificationType.
        if 'type' in kwargs and isinstance(kwargs['type'], basestring):
            kwargs['type'], _ = NotificationType.objects.get_or_create(
                name=kwargs['type'])

        # If a group is provided (and its truthy), use that. Otherwise create
        # a new group if more than one account is going to be notified.
        if 'group' not in kwargs or not kwargs['group']:
            if len(accounts) > 1:
                kwargs['group'] = NotificationGroup.objects.create()
            else:
                kwargs['group'] = None

        notifications = []
        for account in accounts:
            notifications.append(Notification.objects.create(
                account=account, **kwargs))
        return notifications

    def create_for_account(self, account, group=False, **kwargs):

        if group:
            kwargs['group'] = NotificationGroup.objects.create()

        return self.create_for_accounts([account, ], **kwargs)[0]

    def for_account(self, account):
        """
        Wrapped into a simpler helper as we may want to change the behaviour
        later to retrieve notifications for sub or parent accounts based on
        the membership.
        """
        return self._user(account=account)

    def _user(self, account=None):
        # XXX: THIS MEANS A QUERY USING for_account WILL RETURN ALL NOTIFICATIONS IF NO ACCOUNT
        if account:
            return Notification.objects(account=account)
        else:
            return Notification.objects

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
        except (Notification.DoesNotExist, ValidationError):
            raise Http404("Notification not found for %s" % kwargs)


SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL = (0, 1, 2, 3)

SEVERITY_CHOICES = (
    (SEVERITY_LOW, 'Low'),
    (SEVERITY_MEDIUM, 'Medium'),
    (SEVERITY_HIGH, 'High'),
    (SEVERITY_CRITICAL, 'Critical'),
)


class Notification(Document):

    meta = {'queryset_class': NotificationQuerySet}

    account = ReferenceField(Account, required=True)
    group = ReferenceField(NotificationGroup, required=False)
    type = ReferenceField(NotificationType, required=True)
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

    def resolve(self):
        """
        If the notification is in a group, update the full notification
        group - including this one. Otherwise update only this notification.
        """

        if not self.group:
            self.resolved = True
            self.save()
            return

        for notification in Notification.objects(group=self.group):
            notification.resolved = True
            notification.save()

    def should_send_email(self):
        return True

    def send_email(self, request=None):

        notifications_count = Notification.objects.for_account(self.account
            ).filter(opened=False, resolved=False).count()

        message = render_to_string('notifications/notification_email.txt', {
            'account': self,
            'notifications_count': notifications_count
        })

        send_mail('ALISS Notifications', message, 'no-reply@aliss.org',
            [self.account.email], fail_silently=False)
