"""
youraliss.tests
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

    def test_youraliss(self):
        from django.core.urlresolvers import reverse

        response = self.client.get(reverse('youraliss'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')
        response = self.client.get(reverse('youraliss'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bob")

        response = self.client.get(reverse('youraliss_account'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your account settings")

        response = self.client.get(reverse('youraliss_curations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recently curated resources")

        response = self.client.get(reverse('youraliss_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lists")

