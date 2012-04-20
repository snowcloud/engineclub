"""
home.tests
"""
from django.conf import settings
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase

class ViewsTestCase(MongoTestCase):
    def setUp(self):
        from accounts.tests import setUpAccounts
        from locations.tests import setUpLocations
        from resources.tests import setUpResources
        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)

        from django.test.client import Client

        self.client = Client()

    def test_home(self):
        from django.core.urlresolvers import reverse
        from enginecab.views import reindex_resources
        reindex_resources(url=settings.TEST_SOLR_URL)

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to ALISS")

        response = self.client.get(reverse('youraliss'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')
        response = self.client.get(reverse('youraliss'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile")

        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('resource_find'),
            data={'kwords': 'green'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'title 1')

    def test_contact(self):
        from django.core.urlresolvers import reverse
        from django.core import mail

        response = self.client.post(reverse('contact'),
            data={'name': 'green'})
        self.assertContains(response, 'Please correct the errors below')

        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse('contact'),
            data={'name': 'green', 'email': 'bert@example.com', 'body': 'email body'})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[ALISS] Contact message from green')
        self.assertTrue(mail.outbox[0].body.find('email body') > -1)

        
