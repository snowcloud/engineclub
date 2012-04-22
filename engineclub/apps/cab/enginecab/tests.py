# -*- coding: utf-8 -*-
"""
enginecab/tests.py
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

    def test_enginecab(self):
        from django.core.urlresolvers import reverse

        response = self.client.get(reverse('cab'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='bob', password='password')
        response = self.client.get(reverse('cab'))
        self.assertEqual(response.status_code, 302)

        self.user_bob.is_staff = True
        self.user_bob.save()

        response = self.client.get(reverse('cab'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Engine Cab")

        response = self.client.get(reverse('cab_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Issues")

        response = self.client.get(reverse('cab_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lists")

        response = self.client.get(reverse('cab_resources'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resources")



