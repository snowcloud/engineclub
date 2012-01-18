from mongoengine.django.tests import MongoTestCase


class NotificationsTestCase(MongoTestCase):

    def setUp(self):

        from engine_groups.models import Account

        self.account1 = Account.objects.create(name="Bob", email="bob@example.com")
        self.account2 = Account.objects.create(name="Alice", email="alice@example.com")

    def test_types(self):

        from Notifications.models import NotificationType

        nt, created = NotificationType.objects.get_or_create(name="expired")

    def test_create(self):

        from notifications.models import Notification, NotificationType

        expired, created = NotificationType.objects.get_or_create(name="expired")

        accounts = [self.account1, self.account2]

        Notification.objects.create_for_accounts(accounts, type=expired,
            severity=1, message='Curation X has expired'
        )

    def test_get_notifications(self):

        from notifications.models import Notification, NotificationType

        expired, created = NotificationType.objects.get_or_create(name="expired")

        self.assertEqual(0, Notification.objects(account=self.account1).count())

        Notification.objects.create_for_accounts([self.account1, ], type=expired,
            severity=1, message='Curation X has expired'
        )

        self.assertEqual(1, Notification.objects(account=self.account1).count())
