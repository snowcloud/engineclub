# -*- coding: utf-8 -*-
"""
stories/tests.py
"""

from django.conf import settings
from ecutils.tests import MongoTestCase
from resources.models import Resource, Curation, add_curation

from accounts.tests import setUpAccounts
from locations.tests import setUpLocations
from resources.tests import setUpResources
from enginecab.views import reindex_accounts, reindex_resources

class ViewsTestCase(MongoTestCase):
    def setUp(self):

        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)

        # reload these to avoid errors.
        self.resource6 = Resource.objects.get(id=self.resource6.id)
        self.resource7 = Resource.objects.get(id=self.resource7.id)

        self.curation1 = Curation(
            outcome='',
            tags=['#aliss-story'],
            note='This is my story, this is my song',
            owner=self.bob)
        self.curation1.item_metadata.update(author=self.bob)
        add_curation(self.resource6, self.curation1)

        self.curation2 = Curation(
            outcome='',
            tags=['#aliss-story'],
            note='Follow the hearts and, you can\'t go wrong',
            owner=self.bob)
        self.curation2.item_metadata.update(author=self.bob)
        add_curation(self.resource7, self.curation2)

        self.jorph.tags = ['#aliss-story']
        self.jorph.save()

        reindex_accounts(url=settings.TEST_SOLR_URL)
        reindex_resources(url=settings.TEST_SOLR_URL)

        from django.test.client import Client
        self.client = Client()

    def test_stories_list(self):
        from django.core.urlresolvers import reverse

        response = self.client.get(reverse('stories_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aliss stories")
        self.assertContains(response, "title 6")
        self.assertContains(response, "jorph")

    def test_stories_detail(self):
        from django.core.urlresolvers import reverse

        response = self.client.get(reverse('stories_detail', args=[self.curation1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "title 6")

