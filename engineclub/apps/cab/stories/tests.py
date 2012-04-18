# -*- coding: utf-8 -*-
"""
stories/tests.py
"""

from django.conf import settings
from mongoengine.django.tests import MongoTestCase
from resources.models import Curation

class ViewsTestCase(MongoTestCase):
    def setUp(self):
        from accounts.tests import setUpAccounts
        from locations.tests import setUpLocations
        from resources.tests import setUpResources
        from enginecab.views import reindex_resources

        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)

        curation = Curation(
            outcome='',
            tags=['#aliss-story'],
            note='This is my story, this is my song',
            owner=self.bob)
        curation.item_metadata.update(author=self.bob)
        self.resource6.add_curation(curation)

        curation = Curation(
            outcome='',
            tags=['#aliss-story'],
            note='Follow the hearts and, you can\'t go wrong',
            owner=self.bob)
        curation.item_metadata.update(author=self.bob)
        self.resource7.add_curation(curation)

        reindex_resources(url=settings.TEST_SOLR_URL)

        from django.test.client import Client
        self.client = Client()

    def test_stories_list(self):
        from django.core.urlresolvers import reverse

        response = self.client.get(reverse('stories_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aliss stories")

