from datetime import datetime

from mongoengine import *
from mongoengine.queryset import QuerySet

from engine_groups.models import Account


class NotificationGroup(Document):
    pass


class NotificationType(Document):
    name = StringField()


class NotificationQuerySet(QuerySet):

    def create_for_accounts(self, accounts, **kwargs):
        """
        Create notifications for a list of accounts. This is done so that
        when a notification if given to a group of people, once one person
        deals with it, we can strike it off for all the others.
        """

        ng = NotificationGroup.objects.create()

        for account in accounts:
            Notification.objects.create(account=account, group=ng, **kwargs)

    def create_for_account(self, account, **kwargs):
        return self.create_for_accounts([account, ], **kwargs)

    def for_account(self, account):
        """
        Wrapped into a simpler helper as we may want to change the behaviour
        later to retrieve notifications for sub or parent accounts based on
        the membership.
        """
        return Notification.objects(account=account)

    def _user(self, account=None):
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
