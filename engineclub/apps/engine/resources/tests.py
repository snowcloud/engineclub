# -*- coding: utf-8 -*-
"""
apps/depot/tests.py
"""

from django.conf import settings
from mongoengine.django.tests import MongoTestCase

from resources.models import Resource, Curation, Location, load_resource_data
from resources.search import lat_lon_to_str
from resources.forms import ShortResourceForm


SOLR_URL = 'http://127.0.0.1:8983/solr'
# # SOLR_URL = settings.SOLR_URL
# SOLR_ROWS = 5 # settings.SOLR_ROWS


def _load_data(resources='resources', locations='locations'):
    """loads fixture data for test Resources"""
    resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, resources), 'rU')
    load_resource_data('resource', resource_data)
    resource_data.close()

def makeResource(data):
    return Resource.objects.create(
        title=title,
        owner=owner)

def setUpLocations(self):
    data = { "id" : "EH151AR", "accuracy" : "6", "postcode" : "EH15 1AR", "district" : "City of Edinburgh", "loc_type" : "POSTCODE", "country_code" : "SCT", "lat_lon" : [ 55.9539, -3.1164 ], "place_name" : "Portobello/Craigmillar, City of Edinburgh" }
    self.loc1 = Location.objects.create(**data)


def setUpResources(self):
    for idx, data in enumerate((
            {'title': 'title 0', 'owner': self.alice, 'tags': ['red', 'blue']},
            {'title': 'title 1', 'owner': self.alice, 'tags': ['blue', 'green']},
            {'title': 'title 2', 'owner': self.alice, 'tags': ['red', 'blue', 'green']},
            {'title': 'title 3', 'owner': self.bob, 'tags': ['red']},
            {'title': 'title 4', 'owner': self.jorph, 'tags': ['blue', 'green']},
            {'title': 'title 5', 'owner': self.jorph, 'tags': ['red', 'blue']},
            {'title': 'title 6', 'owner': self.hugo, 'tags': ['blue']},
            {'title': 'title 7', 'owner': self.group, 'tags': ['blue']},
            {'title': 'title 8', 'owner': self.group, 'tags': ['blue', 'pink']},
            )):
        res =  Resource.objects.create(**data)
        setattr(self, 'resource%s' % idx, res)
    self.resource0.locations.append(self.loc1)
    self.resource1.locations.append(self.loc1)

class ResourceTest(MongoTestCase):
            
    def setUp(self):
        from accounts.tests import setUpAccounts
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
        title = u'test title 7'
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



class SearchTest(MongoTestCase):
            
    def setUp(self):
        from accounts.tests import setUpAccounts
        from enginecab.views import reindex_resources

        setUpAccounts(self)
        setUpLocations(self)
        setUpResources(self)        
        reindex_resources(url=SOLR_URL)

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





