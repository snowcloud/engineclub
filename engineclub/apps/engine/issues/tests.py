from mongoengine.django.tests import MongoTestCase

class IssuesTestCase(MongoTestCase):

    def setUp(self):
        from accounts.tests import setUpAccounts
        from locations.tests import setUpLocations
        from resources.tests import setUpResources
        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)

class ApiTestCase(IssuesTestCase):

    def test_create(self):

        from issues.models import Issue, \
            SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL

        # create issues
        issue, created = Issue.objects.get_or_create(
            message = 'blah blah',
            severity = SEVERITY_LOW,
            reporter = self.bob,
            related_document=self.resource1
            )
        issue.curators = [self.emma, self.hugo]
        issue.save()
        self.assertEqual(issue.related_document.title, 'title 1')
        self.assertEqual(issue.resource_owner, self.alice)

        issue2, created = Issue.objects.get_or_create(
            message = 'more blah blah',
            severity = SEVERITY_MEDIUM,
            reporter = self.alice,
            related_document=self.resource3
            )
        issue2.curators = [self.jorph, self.hugo]
        issue2.save()
        self.assertEqual(issue2.related_document.title, 'title 3')
        self.assertEqual(issue2.resource_owner, self.bob)

        self.assertTrue(Issue.objects.count() == 2)


        # send accountmessages

        # add some comments

        # check messages sent

        # get messages for an account
        self.assertEqual(2, Issue.objects.for_account(self.bob).count())
        self.assertEqual(1, Issue.objects.for_account(self.jorph).count())

        # get issues for an account

        # resolve issue

        # check messages

        # check resource moderation


class ViewsTestCase(IssuesTestCase):

    def setUp(self):
        super(ViewsTestCase, self).setUp()

        from django.test.client import Client

        self.client = Client()

    def test_no_issues(self):

        from django.core.urlresolvers import reverse

        # Can't access when we are not logged in.
        response = self.client.get(reverse('issue_list'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')

        response = self.client.get(reverse('issue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no alerts")

    def test_report(self):

        from django.core.urlresolvers import reverse
        from resources.models import Resource
        from issues.models import Issue, \
            SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL


        # Can't access when we are not logged in.
        response = self.client.get(reverse(
            'resource_report',
            kwargs={'object_id': self.resource1.id}))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')

        response = self.client.get(reverse(
            'resource_report',
            kwargs={'object_id': self.resource1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ALISS: report %s" % self.resource1.title)

        response = self.client.post(
            reverse(
                'resource_report',
                kwargs={'object_id': self.resource1.id}),
            data={'severity': '1', 'message': 'I am reporting this now.'})
        self.assertEqual(response.status_code, 302)

        issue = Issue.objects.first()
        self.assertEqual(issue.severity, 1)
        self.assertEqual(issue.message, 'I am reporting this now.')
        self.assertEqual(issue.reporter, self.bob)
        self.assertEqual(issue.related_document, self.resource1)

        response = self.client.post(reverse('issue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'I am reporting this now.')

        response = self.client.post(reverse('issue_detail', kwargs={'object_id': issue.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'I am reporting this now.')




# class ApiTestCase(IssuesTestCase):

#     def test_types(self):

#         from issues.models import AlertType

#         nt, _ = AlertType.objects.get_or_create(name="expired")

#     def test_create(self):

#         from issues.models import Alert, AlertType

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

#         from issues.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         self.assertEqual(0, Alert.objects.for_account(self.bob).count())

#         Alert.objects.create_for_account(self.bob, type=expired,
#             severity=1, message='Curation X has expired'
#         )

#         self.assertEqual(1, Alert.objects.for_account(self.bob).count())

#     def test_get_member_alerts(self):

#         from issues.models import Alert, AlertType

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

#         from issues.models import Alert, AlertType

#         expired, _ = AlertType.objects.get_or_create(name="expired")

#         Alert.objects.create_for_accounts([self.bob, self.alice],
#             type=expired, severity=3, message='Curation X has expired')

#         bob_notification, = Alert.objects.for_account(self.bob)
#         alice_notification, = Alert.objects.for_account(self.alice)

#         self.assertEqual(bob_notification.group, alice_notification.group)

#     def test_severity(self):

#         from issues.models import Alert, AlertType

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

#         from issues.models import Alert, AlertType

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
#         from issues.models import Alert, AlertType

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
#         from issues.models import Alert, AlertType

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

#         from resources.models import Resource

#         self.resource, _ = Resource.objects.get_or_create(
#             __raw__={'_id': u'4d135708e999fb30d8000007'},
#             defaults={'title': "Testing resource", 'owner': self.bob})

#         from django.test.client import Client
#         self.client = Client()

#     def test_annon_report(self):

#         from django.core.urlresolvers import reverse
#         from issues.models import Alert, SEVERITY_MEDIUM

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
#         from issues.models import Alert, SEVERITY_HIGH

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
