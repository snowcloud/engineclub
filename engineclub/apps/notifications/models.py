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

        ng = NotificationGroup.objects.create()

        for account in accounts:
            Notification.objects.create(account=account, group=ng, **kwargs)


SEVERITY_CHOICES = (
    (0, 'Low'),
    (1, 'Medium'),
    (2, 'High'),
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

    def __unicode__(self):
        return self.message
