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

    def test_password_reset(self):
        from django.core.urlresolvers import reverse
        from django.core import mail
        
        response = self.client.post(reverse('password_reset'),
            data={})
        self.assertContains(response, 'This field is required')
        response = self.client.post(reverse('password_reset'),
            data={'email': 'asssdasdf@asasdf.com'})
        self.assertContains(response, 'That e-mail address doesn&#39;t have an associated user account. Are you sure you&#39;ve registered?')

        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse('password_reset'),
            data={'email': 'bob@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on example.com')
        self.assertTrue(mail.outbox[0].body.find('http://example.com/reset/') > -1)

        site = 'http://example.com'
        url = [line for line in mail.outbox[0].body.split('\n') if line.startswith(site)][0]
        response = self.client.post(
                url[len(site):], 
                data={'new_password1': 'blug', 'new_password2': 'blug'})
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='blug')
        response = self.client.get(reverse('youraliss'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile")

