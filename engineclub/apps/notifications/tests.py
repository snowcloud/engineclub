from mongoengine.django.tests import MongoTestCase


class NotificationsTestCase(MongoTestCase):

    def setUp(self):
        """
        Create two test accounts and a parent account with alice being a
        member.
        """

        from django.contrib.auth.models import User

        from engine_groups.models import Account, Membership

        # Admin user is 1, bob and alice follow from there.
        self.bob = Account.objects.create(name="Bob", email="bob@example.com", local_id="2")
        self.alice = Account.objects.create(name="Alice", email="alice@example.com", local_id="3")

        self.user_bob = User.objects.create_user('bob', email="bob@example.com",
            password='password')
        self.user_alice = User.objects.create_user('alice', email="alice@example.com",
            password='password')

        self.company = Account.objects.create(name="company", email="org@example.com")

        Membership.objects.create(parent_account=self.company, member=self.alice)


class ApiTestCase(NotificationsTestCase):

    def test_types(self):

        from Notifications.models import NotificationType

        nt, _ = NotificationType.objects.get_or_create(name="expired")

    def test_create(self):

        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")

        accounts = [self.bob, self.alice]

        Notification.objects.create_for_accounts(accounts, type=expired,
            severity=1, message='Curation X has expired'
        )

    def test_get_notifications(self):

        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")

        self.assertEqual(0, Notification.objects.for_account(self.bob).count())

        Notification.objects.create_for_account(self.bob, type=expired,
            severity=1, message='Curation X has expired'
        )

        self.assertEqual(1, Notification.objects.for_account(self.bob).count())

    def test_get_member_notifications(self):

        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")
        incorrect, _ = NotificationType.objects.get_or_create(name="incorrect")

        self.assertEqual(0, Notification.objects.for_account(self.alice).count())

        # Create a notification for alice and orgnaisation1
        Notification.objects.create_for_accounts([self.alice, self.company],
            type=expired, severity=1, message='Curation X is going to expire')

        # Create a notification for orgnanisation1
        Notification.objects.create_for_account(self.company,
            type=incorrect, severity=1, message='Curation Y is incorrect')

        # Create a notification for alice
        Notification.objects.create_for_account(self.alice,
            type=expired, severity=1, message='Curation Z is going to expire')

        self.assertEqual(2, Notification.objects.for_account(self.alice).count())
        self.assertEqual(2, Notification.objects.for_account(self.company).count())

    def test_group_notifications(self):

        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")

        Notification.objects.create_for_accounts([self.bob, self.alice],
            type=expired, severity=3, message='Curation X has expired')

        bob_notification, = Notification.objects.for_account(self.bob)
        alice_notification, = Notification.objects.for_account(self.alice)

        self.assertEqual(bob_notification.group, alice_notification.group)

    def test_severity(self):

        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")

        for i in range(4):
            for _ in range(i + 1):
                Notification.objects.create_for_account(self.alice,
                    type=expired, severity=i, message='Expiration warning')

        self.assertEqual(Notification.objects.low(self.alice).count(), 1)
        self.assertEqual(Notification.objects.medium(self.alice).count(), 2)
        self.assertEqual(Notification.objects.high(self.alice).count(), 3)
        self.assertEqual(Notification.objects.critical(self.alice).count(), 4)


class ViewsTestCase(NotificationsTestCase):

    def setUp(self):
        super(ViewsTestCase, self).setUp()

        from django.test.client import Client

        self.client = Client()

    def test_no_notifications(self):

        from django.core.urlresolvers import reverse

        # Can't access when we are not logged in.
        response = self.client.get(reverse('notifications-list'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')

        response = self.client.get(reverse('notifications-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You don't have any notifications")

    def test_notifications_list(self):

        from django.core.urlresolvers import reverse
        from notifications.models import Notification, NotificationType

        expired, _ = NotificationType.objects.get_or_create(name="expired")

        Notification.objects.create_for_account(self.bob, type=expired,
            severity=1, message='Curation X has expired'
        )

        self.client.login(username='bob', password='password')

        response = self.client.get(reverse('notifications-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curation X has expired")
