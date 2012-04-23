# -*- coding: utf-8 -*-
"""
apps/depot/tests.py
"""

from django.conf import settings
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase

from resources.models import Resource, Curation, add_curation, load_resource_data
from resources.search import lat_lon_to_str
from resources.forms import ShortResourceForm


def _load_data(resources='resources', locations='locations'):
    """loads fixture data for test Resources"""
    resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, resources), 'rU')
    load_resource_data('resource', resource_data)
    resource_data.close()

def makeResource(data):
    return Resource.objects.create(
        title=title,
        owner=owner)

def setUpResources(self):
    for idx, data in enumerate((
            {'title': 'title 0', 'owner': self.alice, 'tags': ['red', 'blue'], 'description': 'This is title 0'},
            {'title': 'title 1', 'owner': self.alice, 'tags': ['blue', 'green'], 'description': 'This is title 1'},
            {'title': 'title 2', 'owner': self.alice, 'tags': ['red', 'blue', 'green'], 'description': 'This is title 2'},
            {'title': 'title 3', 'owner': self.bob, 'tags': ['red'], 'description': 'This is title 3'},
            {'title': 'title 4', 'owner': self.jorph, 'tags': ['blue', 'green'], 'description': 'This is title 4'},
            {'title': 'title 5', 'owner': self.jorph, 'tags': ['red', 'blue'], 'description': 'This is title 5'},
            {'title': 'title 6', 'owner': self.hugo, 'tags': ['blue'], 'description': 'This is title 6'},
            {'title': 'title 7', 'owner': self.group, 'tags': ['blue'], 'description': 'This is title 7'},
            {'title': 'title 8', 'owner': self.group, 'tags': ['blue', 'pink'], 'description': 'This is title 8'},
            )):
        res =  Resource.objects.create(**data)
        setattr(self, 'resource%s' % idx, res)
    self.resource0.locations.append(self.loc1)
    self.resource1.locations.append(self.loc1)

class ResourceTest(MongoTestCase):
            
    def setUp(self):
        from accounts.tests import setUpAccounts
        from locations.tests import setUpLocations
        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)

    def test_resources(self):
        self.assertEqual(Resource.objects.count(), 9)
        
    def test_newresource(self):
        """
        Tests create a new resource.
        """
        # uri = u'http://test.example.com/1/'
        title = u'test title 99'
        author = self.emma
        resource, created = Resource.objects.get_or_create(__raw__={'_id': u'4d135708e999fb30d8000007'}, defaults={'title': title, 'owner': author})
        resource.item_metadata.author = author
        self.assertTrue(created)
        # self.assertEqual(unicode(resource.id), u'4d135708e999fb30d8000001')
        self.assertEqual(resource.title, title)
        self.assertEqual(resource.item_metadata.author, author)
    

    def test_tags(self):
        """docstring for test_tags"""

        resources = Resource.objects(tags='red')
        self.assertEqual(len(resources), 4)
        # 6 tags contain blue OR red
        resources = Resource.objects(tags__in=['blue', 'red'])
        self.assertEqual(len(resources), 9)
        # 2 tags contain blue AND red
        resources = Resource.objects(tags__all=['blue', 'red'])
        self.assertEqual(len(resources), 3)
    
#     def test_tagslist(self):
#         """docstring for test_tagslist"""
#         # self.db = self._load_data()
#         self.assertEqual(Resource.objects.count(), 6)
#         for resource in Resource.objects:
#             resource.make_keys([])
#             resource.save()
#         update_keyword_index()
#         self.assertEqual(Resource.objects.count(), 6)
#         results = get_db().keyword.find( { "_id" : re.compile('^Bl*', re.IGNORECASE)} ) #.count()
#         self.assertEqual([i['_id'] for i in results], [u'blue'])
      
#     def test_geo(self):
#         """docstring for test_geo"""
#         # db = self._load_data()
#         self.assertEqual(Resource.objects.count(), 6)
#         for resource in Resource.objects:
#             resource.make_keys([])
#             resource.save()
#             # this is making a second object
#             # SEE EVERNOTE- PROB IF USING STRING AS ID- USE OBJECTID
#         update_keyword_index()
#         results = get_nearest('50', -3.00, categories=['blue']) # takes float or string for lat, lon
#         print results
#         for r in results[0]['resources']:
#             print r.title, r.tags, r.index_keys
#         self.assertEqual(Resource.objects.count(), 6)
#         self.assertEqual(len(results), 1)
#         self.assertEqual(len(results[0]['resources']), 1)


# class ViewTest(MongoTestCase):


#     def test_popup(self):
#         import urllib
        
#         url = '/depot/resource/add/%3Fpopup%3Dtrue%26title%3DALISS%253A%2520Password%2520reset%2520successful%26page%3Dhttp%253A%252F%252F127.0.0.1%253A8080%252Fpassword_reset%252Fdone%252F%26t%3DWe%27ve%2520e-mailed%2520you%2520instructions%2520for%2520setting%2520your%2520password%2520to%2520the%2520e-mail%2520address%2520you%2520submitted.%2520You%2520should%2520be%2520receiving%2520it%2520shortly.%257C%257C%257C%257C'
#         print url
#         print urllib.unquote(url)


class SearchTest(MongoTestCase):
            
    def setUp(self):
        from accounts.tests import setUpAccounts
        from locations.tests import setUpLocations
        from enginecab.views import reindex_resources

        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)        
        reindex_resources(url=settings.TEST_SOLR_URL)

    def test_postcode(self):
        from resources.search import find_by_place_or_kwords

        postcode = 'EH15 1AR'
        # [55.953899999999997, -3.1164000000000001]

        lat_lon, results = find_by_place_or_kwords(postcode, '')
        result = iter(results).next()
        self.assertEqual(result['title'], 'title 0')
        lat_lon, results = find_by_place_or_kwords(postcode, 'green')
        result = iter(results).next()
        self.assertEqual(result['title'], 'title 1')
        lat_lon, results = find_by_place_or_kwords('', 'pink')
        self.assertEqual(lat_lon, None)
        result = iter(results).next()
        self.assertEqual(result['title'], 'title 8')

    def test_curation(self):
        from resources.search import find_by_place_or_kwords

        # setting resource failed - no idea why, seems a valid object
        # reloading works
        self.resource6 = Resource.objects.get(id=self.resource6.id)
        curation = Curation(
            outcome='',
            tags=['blah'],
            note='bob curated this',
            owner=self.bob,
            )
        curation.item_metadata.update(author=self.bob)
        add_curation(self.resource6, curation)

        lat_lon, results = find_by_place_or_kwords('', 'blah')
        self.assertEqual(lat_lon, None)
        result = iter(results).next()
        self.assertEqual(result['title'], 'title 6')




