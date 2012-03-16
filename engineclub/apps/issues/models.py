from datetime import datetime

from django.core.mail import send_mail
from django.http import Http404
from django.template.loader import render_to_string
from mongoengine import *
from mongoengine.queryset import QuerySet
from mongoengine.base import ValidationError

from accounts.models import Account

SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL = (0, 1, 2, 3)

SEVERITY_CHOICES = (
    (SEVERITY_LOW, 'Low'),
    (SEVERITY_MEDIUM, 'Medium'),
    (SEVERITY_HIGH, 'High'),
    (SEVERITY_CRITICAL, 'Critical'),
)

class Issue(Document):

    meta = {
       'allow_inheritance': False
    }

    message = StringField(required=True)
    severity = IntField(choices=SEVERITY_CHOICES, required=True)
    reporter = ReferenceField(Account, required=True)
    resource_owner = ReferenceField(Account)
    curators = ListField(ReferenceField(Account), default=list)
    reported_at = DateTimeField(default=datetime.now)
    resolved = BooleanField(default=False)
    related_document = GenericReferenceField()

    def save(self, *args, **kwargs):
        if self.related_document:
            self.resource_owner = self.related_document.owner
        super(Issue, self).save(*args, **kwargs)


class IssueComment(EmbeddedDocument):

    meta = {
        'allow_inheritance': False
    }

class AccountMessage(Document):

    meta = {
        'allow_inheritance': False
    }

    to_account = ReferenceField(Account, required=True)




###############################################################

# class OldTicket(Document):

#     meta = {
#         'allow_inheritance': False
#     }


# class AlertType(Document):

#     meta = {
#         'allow_inheritance': False
#     }

#     name = StringField()

#     def __unicode__(self):
#         return self.name


# class AlertQuerySet(QuerySet):

#     def create_for_accounts(self, accounts, **kwargs):
#         """
#         Create alerts for a list of accounts. This is done so that
#         when a notification if given to a issue of people, once one person
#         deals with it, we can strike it off for all the others.
#         """

#         # For convenience allow type to be given as a string, and we will
#         # automaticlally lookup/create the AlertType.
#         if 'type' in kwargs and isinstance(kwargs['type'], basestring):
#             kwargs['type'], _ = AlertType.objects.get_or_create(
#                 name=kwargs['type'])

#         # If a issue is provided (and its truthy), use that. Otherwise create
#         # a new issue if more than one account is going to be notified.
#         if 'issue' not in kwargs or not kwargs['issue']:
#             if len(accounts) > 1:
#                 kwargs['issue'] = OldTicket.objects.create()
#             else:
#                 kwargs['issue'] = None

#         alerts = []
#         for account in accounts:
#             alerts.append(Alert.objects.create(
#                 account=account, **kwargs))
#         return alerts

#     def create_for_account(self, account, create_issue=False, **kwargs):

#         if create_issue:
#             kwargs['issue'] = OldTicket.objects.create()

#         return self.create_for_accounts([account, ], **kwargs)[0]

#     def for_account(self, account):
#         """
#         Wrapped into a simpler helper as we may want to change the behaviour
#         later to retrieve alerts for sub or parent accounts based on
#         the membership.
#         """
#         return self._user(account=account)

#     def _user(self, account=None):
#         # XXX: THIS MEANS A QUERY USING for_account WILL RETURN ALL NOTIFICATIONS IF NO ACCOUNT
#         if account:
#             return Alert.objects(account=account)
#         else:
#             return Alert.objects

#     def low(self, user=None):
#         return self._user(user)(severity=SEVERITY_LOW)

#     def medium(self, user=None):
#         return self._user(user)(severity=SEVERITY_MEDIUM)

#     def high(self, user=None):
#         return self._user(user)(severity=SEVERITY_HIGH)

#     def critical(self, user=None):
#         return self._user(user)(severity=SEVERITY_CRITICAL)

#     def get_or_404(self, **kwargs):
#         try:
#             return self.get(**kwargs)
#         except (Alert.DoesNotExist, ValidationError):
#             raise Http404("Alert not found for %s" % kwargs)


# class Alert(Document):

#     meta = {
#         'queryset_class': AlertQuerySet,
#         'allow_inheritance': False
#     }

#     account = ReferenceField(Account, required=True)
#     issue = ReferenceField(OldTicket, required=False)
#     type = ReferenceField(AlertType, required=True)
#     severity = IntField(choices=SEVERITY_CHOICES, required=True)
#     datetime = DateTimeField(default=datetime.now)
#     origin = ReferenceField(Account, required=False)
#     message = StringField()
#     opened = BooleanField(default=False)
#     resolved = BooleanField(default=False)
#     related_document = GenericReferenceField()

#     def __unicode__(self):
#         return self.message

#     def mark_read(self):
#         self.opened = True
#         self.save()

#     # def resolve(self):
#     #     """
#     #     If the alert is in a issue, update the full notification
#     #     issue - including this one. Otherwise update only this notification.
#     #     """

#     #     if not self.issue:
#     #         self.resolved = True
#     #         self.save()
#     #         return

#     #     for notification in Alert.objects(issue=self.issue):
#     #         notification.resolved = True
#     #         notification.save()

#     def should_send_email(self):
#         return True

#     def send_email(self, request=None):

#         alerts_count = Alert.objects.for_account(self.account
#             ).filter(opened=False, resolved=False).count()

#         message = render_to_string('issues/alert_email.txt', {
#             'account': self.account,
#             'alerts_count': alerts_count
#         })

#         send_mail('ALISS Alerts', message, 'no-reply@aliss.org',
#             [self.account.email], fail_silently=False)
