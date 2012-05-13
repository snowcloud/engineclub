# -*- coding: utf-8 -*-
"""
enginecab/tests.py
"""

from django.conf import settings
from django.core.urlresolvers import reverse

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

    def test_tagprocessor(self):
        from enginecab.models import TagProcessor
        
        TESTTAGS = ['blah', 'lrg', '123', 'UPPer', 'KEEPieUppie', '   ', 'please, SPLIT,me;up,   now ']
        TESTTAG_SPLIT = ['blah', 'lrg', '123', 'UPPer', 'KEEPieUppie', 'please', 'SPLIT', 'me', 'up', 'now']
        TESTTAG_SPLIT_LOWER = ['blah', 'lrg', '123', 'upper', 'KEEPieUppie', 'please', 'split', 'me', 'up', 'now']

        tp = TagProcessor(TESTTAGS)
        self.assertEqual(tp.tags, TESTTAGS)
        self.assertEqual(tp.split(True).tags, TESTTAG_SPLIT)
        self.assertEqual(tp.lower(True, ['KEEPieUppie']).tags, TESTTAG_SPLIT_LOWER)

        tp.tags = TESTTAGS
        self.assertEqual(tp.split(True).lower(True, ['KEEPieUppie']).tags, TESTTAG_SPLIT_LOWER)

    def test_tags(self):
        self.client.login(username='bob', password='password')

        response = self.client.get(reverse('cab_tags'))
        self.assertEqual(response.status_code, 302)

        self.user_bob.is_staff = True
        self.user_bob.save()

        response = self.client.get(reverse('cab_tags'))
        self.assertEqual(response.status_code, 302)

        self.user_bob.is_superuser = True
        self.user_bob.save()

        response = self.client.get(reverse('cab_tags'))
        self.assertEqual(response.status_code, 200)

        LOWERTAG = 'green'
        UPPERTAG = LOWERTAG.upper()
        self.assertContains(response, LOWERTAG)

        # cab_tags will have a user message after each process, with tag in it
        # so can't just test for presence/absence of tag
        # tags in list are in quotes, so using that
        
        response = self.client.get(reverse('cab_tags_upper', args=[LOWERTAG]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('cab_tags'))
        self.assertNotContains(response, '"%s"' % LOWERTAG)
        self.assertContains(response, '"%s"' % UPPERTAG)

        response = self.client.get(reverse('cab_tags_lower', args=[UPPERTAG]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('cab_tags'))
        self.assertNotContains(response, '"%s"' % UPPERTAG)
        self.assertContains(response, '"%s"' % LOWERTAG)

        response = self.client.get(reverse('cab_tags_remove', args=[LOWERTAG]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('cab_tags'))
        self.assertNotContains(response, '"%s"' % UPPERTAG)
        self.assertNotContains(response, '"%s"' % LOWERTAG)
