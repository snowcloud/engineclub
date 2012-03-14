# from mongoengine.django.tests import MongoTestCase


# class AlertsTestCase(MongoTestCase):

#     def setUp(self):
#         """
#         Create two test accounts and a parent account with alice being a
#         member.
#         """

#         from django.contrib.auth.models import User

#         from accounts.models import Account, Membership

#         # Create three normal contrib.auth users
#         self.user_bob = User.objects.create_user('bob', email="bob@example.com",
#             password='password')
#         self.user_alice = User.objects.create_user('alice', email="alice@example.com",
#             password='password')
#         self.user_company = User.objects.create_user('company',
#             email="company@example.com", password="password")

#         # Create three mongodb accounts and related them to the contrib.auth
#         # user accounts.
#         self.bob = Account.objects.create(name="Bob", email="bob@example.com",
#             local_id=str(self.user_bob.id))
#         self.alice = Account.objects.create(name="Alice",
#             email="alice@example.com", local_id=str(self.user_alice.id))
#         self.company = Account.objects.create(name="company",
#             email="org@example.com", local_id=str(self.user_company.id))

#         # Add alice to the company, so she is a "sub account"
#         Membership.objects.create(parent_account=self.company, member=self.alice)


# class ApiTestCase(AlertsTestCase):

#     def test_types(self):

#         from tickets.models import AlertType

#         nt, _ = AlertType.objects.get_or_create(name="expired")

#     def test_create(self):

#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         accounts = [self.bob, self.alice]

#         Alert.objects.create_for_accounts(accounts, type=expired,
#             severity=1, message='Curation X has expired'
#         )

#         Alert.objects.create_for_accounts(accounts, type="expired",
#             severity=1, message='Curation X has expired'
#         )

#         Alert.objects.create_for_accounts(accounts, type="test",
#             severity=1, message='Curation X has expired'
#         )

#         test, created = AlertType.objects.get_or_create(name="expired")
#         self.assertFalse(created)

#     def test_get_alerts(self):

#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         self.assertEqual(0, Alert.objects.for_account(self.bob).count())

#         Alert.objects.create_for_account(self.bob, type=expired,
#             severity=1, message='Curation X has expired'
#         )

#         self.assertEqual(1, Alert.objects.for_account(self.bob).count())

#     def test_get_member_alerts(self):

#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")
#         incorrect, _ = AlertType.objects.get_or_create(name="incorrect")

#         self.assertEqual(0, Alert.objects.for_account(self.alice).count())

#         # Create a notification for alice and orgnaisation1
#         Alert.objects.create_for_accounts([self.alice, self.company],
#             type=expired, severity=1, message='Curation X is going to expire')

#         # Create a notification for orgnanisation1
#         Alert.objects.create_for_account(self.company,
#             type=incorrect, severity=1, message='Curation Y is incorrect')

#         # Create a notification for alice
#         Alert.objects.create_for_account(self.alice,
#             type=expired, severity=1, message='Curation Z is going to expire')

#         self.assertEqual(2, Alert.objects.for_account(self.alice).count())
#         self.assertEqual(2, Alert.objects.for_account(self.company).count())

#     def test_group_alerts(self):

#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         Alert.objects.create_for_accounts([self.bob, self.alice],
#             type=expired, severity=3, message='Curation X has expired')

#         bob_notification, = Alert.objects.for_account(self.bob)
#         alice_notification, = Alert.objects.for_account(self.alice)

#         self.assertEqual(bob_notification.group, alice_notification.group)

#     def test_severity(self):

#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         for i in range(4):
#             for _ in range(i + 1):
#                 Alert.objects.create_for_account(self.alice,
#                     type=expired, severity=i, message='Expiration warning')

#         self.assertEqual(Alert.objects.low(self.alice).count(), 1)
#         self.assertEqual(Alert.objects.medium(self.alice).count(), 2)
#         self.assertEqual(Alert.objects.high(self.alice).count(), 3)
#         self.assertEqual(Alert.objects.critical(self.alice).count(), 4)

#     def test_related_document(self):

#         from tickets.models import Alert, AlertType

#         account, _ = AlertType.objects.get_or_create(name="account")

#         notification = Alert.objects.create_for_account(self.alice,
#             type=account, severity=1, message="Password about to expire",
#             related_document=self.alice)

#         self.assertEqual(notification.related_document, self.alice)


# class ViewsTestCase(AlertsTestCase):

#     def setUp(self):
#         super(ViewsTestCase, self).setUp()

#         from django.test.client import Client

#         self.client = Client()

#     def test_no_alerts(self):

#         from django.core.urlresolvers import reverse

#         # Can't access when we are not logged in.
#         response = self.client.get(reverse('alerts-list'))
#         self.assertEqual(response.status_code, 302)

#         self.client.login(username='bob', password='password')

#         response = self.client.get(reverse('alerts-list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "You don't have any alerts")

#     def test_alerts_list(self):

#         from django.core.urlresolvers import reverse
#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")
#         account, _ = AlertType.objects.get_or_create(name="account")

#         Alert.objects.create_for_account(self.bob, type=expired,
#             severity=1, message='Curation X has expired')

#         Alert.objects.create_for_account(self.bob,
#             type=account, severity=1, message="Password about to expire",
#             related_document=self.bob)

#         self.client.login(username='bob', password='password')

#         response = self.client.get(reverse('alerts-list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Curation X has expired")
#         self.assertContains(response, "Bob")

#     def test_detail_view(self):

#         from django.core.urlresolvers import reverse
#         from tickets.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         n = Alert.objects.create_for_account(self.bob, type=expired,
#             severity=1, message='Curation X has expired')

#         self.client.login(username='bob', password='password')

#         response = self.client.get(reverse('alerts-detail', args=["NOTREAL", ]))
#         self.assertEqual(response.status_code, 404)

#         response = self.client.get(reverse('alerts-detail', args=[str(n.id), ]))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Curation X has expired")


# class ReportingTestCase(AlertsTestCase):

#     def setUp(self):
#         super(ReportingTestCase, self).setUp()

#         from depot.models import Resource

#         self.resource, _ = Resource.objects.get_or_create(
#             __raw__={'_id': u'4d135708e999fb30d8000007'},
#             defaults={'title': "Testing resource", 'owner': self.bob})

#         from django.test.client import Client
#         self.client = Client()

#     def test_annon_report(self):

#         from django.core.urlresolvers import reverse
#         from tickets.models import Alert, SEVERITY_MEDIUM

#         # Check there are no alerts.
#         self.assertEqual(Alert.objects.count(), 0)

#         # Trigger the report, which will add a notification for the user
#         # so they know it has been submitted
#         report_url = reverse('resource-report', args=[self.resource.id])
#         response = self.client.post(report_url, {
#             'message': 'The resource contains incorrect information.'
#         }, follow=True)
#         self.assertEqual(response.status_code, 200)

#         # Bob should have one notification, because he is the owner of the
#         # resource.
#         alerts = Alert.objects.for_account(self.bob)
#         self.assertEqual(len(alerts), 1)
#         self.assertEqual(alerts[0].related_document, self.resource)
#         self.assertEqual(alerts[0].severity, SEVERITY_MEDIUM)
#         self.assertEqual(alerts[0].group, None)

#     def test_user_report(self):

#         from django.core.urlresolvers import reverse
#         from tickets.models import Alert, SEVERITY_HIGH

#         self.client.login(username='alice', password='password')

#         # Check there are no alerts.
#         self.assertEqual(Alert.objects.count(), 0)

#         # Trigger the report, which will add a notification for the user
#         # so they know it has been submitted
#         report_url = reverse('resource-report', args=[self.resource.id])
#         response = self.client.post(report_url, {
#             'message': 'The resource contains incorrect information.'
#         }, follow=True)
#         self.assertEqual(response.status_code, 200)

#         # Check the notification is in the list for the user
#         response = self.client.get(reverse('alerts-list',))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Report submitted")

#         # Alice should have one notification that is bound to the resource.
#         # This notification shows that she submitted the report and can then
#         # track it later.
#         alice_alerts = Alert.objects.for_account(self.alice)
#         self.assertEqual(len(alice_alerts), 1)
#         alice_notification = alice_alerts[0]
#         self.assertEqual(alice_notification.related_document, self.resource)

#         # Bob should have one notification, because he is the owner of the
#         # resource.
#         bob_alerts = Alert.objects.for_account(self.bob)
#         self.assertEqual(len(bob_alerts), 1)
#         bob_notification = bob_alerts[0]
#         self.assertEqual(bob_notification.related_document, self.resource)
#         self.assertEqual(bob_notification.severity, SEVERITY_HIGH)

#         # Check the two alerts are in the same group.
#         self.assertEqual(alice_notification.group, bob_notification.group)
