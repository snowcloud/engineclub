# -*- coding: utf-8 -*-
"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Resource, Location, load_resource_data, \
    get_place_for_postcode, lat_lon_to_str
from depot.forms import ShortResourceForm
from mongoengine import connect
from mongoengine.connection import _get_db as get_db

import re

from django.test.simple import *
from django.test import TransactionTestCase

TEST_DB_NAME = 'test_db2'
DB_NAME = 'test_db'
SOLR_URL = 'http://127.0.0.1:8983/solr'
# SOLR_URL = settings.SOLR_URL

TEST_LOCS = {
    'ellon': '57.365287, -2.070642',
    'peterheid': '57.584806, -1.875630',
    'keith': '57.7036280142534, -2.85720247750133',
    'carnoustie': '56.503836, -2.699406',
    'downing st': '51.503541, -0.127670' # SW1A 2AA
}

def _load_data(resources='resources', locations='locations'):
    """loads fixture data for test Resources"""
    resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, resources), 'rU')
    load_resource_data('resource', resource_data)
    resource_data.close()
    # print Resource.objects.count()
    # for resource in Resource.objects:
    #     resource.save()
    # print Resource.objects.count()
    
    
    # for resource in Resource.objects:
    #     locs = []
    #     for loc in resource.locations:
    #         print 'r'
    #     resource.locations = locs
    #     resource.save()
    #
    
    # no Locations while we refactor them
    
    # resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, locations), 'rU')
    # load_resource_data('location', resource_data)
    # resource_data.close()
    
class MongoDBTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        db_name = TEST_DB_NAME
        connect(db_name)
        print 'Creating test-databasey: ' + db_name
        _load_data()
        return db_name

    def teardown_databases(self, db_name, **kwargs):
        from pymongo import Connection
        conn = Connection()
        conn.drop_database(db_name)
        print 'Dropping test-databasey: ' + db_name

class MongoDBRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        db_name = DB_NAME
        connect(db_name)
        print 'Using test_db: ' + db_name
        # _load_data()
        return db_name

    def teardown_databases(self, db_name, **kwargs):
        # from pymongo import Connection
        # conn = Connection()
        # conn.drop_database(db_name)
        print 'Closing test-db: ', db_name, ' (data intact)'


class ResourceTest(TransactionTestCase):
    
        
    def setUp(self):
        if Resource.objects.count() == 0:
            self.db = _load_data()

    def tearDown(self):
        Resource.drop_collection()
        Location.drop_collection()
    
    def test_resources(self):
        title = u'title 2'
        url = u'http://test.example.com/2/'
        self.assertEqual(Resource.objects.count(), 6)
        # resource = Resource.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
        # self.assertEqual(resource.id, u'4d135708e999fb30d8000001')
        # self.assertEqual(resource.item_metadata.author, u'1')
        # get an resource with a resource with this url
        # resources could share a url ?
        resource = Resource.objects.get(url=url)
        self.assertEqual(resource.title, title)
        
    def test_newresource(self):
        """
        Tests create a new resource.
        """
        # uri = u'http://test.example.com/1/'
        title = u'test title 7'
        author = u"1"
        resource, created = Resource.objects.get_or_create(__raw__={'_id': u'4d135708e999fb30d8000007'}, defaults={'title': title})
        resource.item_metadata.author = author
        self.assertTrue(created)
        # self.assertEqual(unicode(resource.id), u'4d135708e999fb30d8000001')
        self.assertEqual(resource.title, title)
        self.assertEqual(resource.item_metadata.author, author)
    
    def test_tags(self):
        """docstring for test_tags"""
        # self._load_data()
        resources = Resource.objects(tags='red')
        # print [(i.title, i.tags) for i in Resource.objects]
        # print 'red resources: ', resources
        self.assertEqual(len(resources), 3)
        # 6 tags contain blue OR red
        resources = Resource.objects(tags__in=['blue', 'red'])
        self.assertEqual(len(resources), 6)
        # 2 tags contain blue AND red
        resources = Resource.objects(tags__all=['blue', 'red'])
        self.assertEqual(len(resources), 2)
    
    def test_tagslist(self):
        """docstring for test_tagslist"""
        # self.db = self._load_data()
        self.assertEqual(Resource.objects.count(), 6)
        for resource in Resource.objects:
            resource.make_keys([])
            resource.save()
        update_keyword_index()
        self.assertEqual(Resource.objects.count(), 6)
        results = get_db().keyword.find( { "_id" : re.compile('^Bl*', re.IGNORECASE)} ) #.count()
        self.assertEqual([i['_id'] for i in results], [u'blue'])
      
    def test_geo(self):
        """docstring for test_geo"""
        # db = self._load_data()
        self.assertEqual(Resource.objects.count(), 6)
        for resource in Resource.objects:
            resource.make_keys([])
            resource.save()
            # this is making a second object
            # SEE EVERNOTE- PROB IF USING STRING AS ID- USE OBJECTID
        update_keyword_index()
        results = get_nearest('50', -3.00, categories=['blue']) # takes float or string for lat, lon
        print results
        for r in results[0]['resources']:
            print r.title, r.tags, r.index_keys
        self.assertEqual(Resource.objects.count(), 6)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]['resources']), 1)

from pysolr import Solr

class SolrTest(TransactionTestCase):
    
    # def test_load_resources(self):
    #     print 'SHOULDN\'T BE IN HERE'
    #     conn = Solr(settings.SOLR_URL)
    #     conn.delete(q='*:*')
    #     
    #     for r in Resource.objects:
    #     #     TODO: SEEMS TO PUT A LIST IN id ???  [u'234lj342lj23l12j3414']
    #         doc = {'id': unicode(r.id), 'res_id': unicode(r.id), 'title': r.title, 'description': r.description, 'keywords': r.index_keys}
    #         # print '%s %s' % (doc['res_id'], unicode(r.id)), r.id
    #         locs = r.get_locations()
    #         if locs:
    #             # print '%s, %s' % (locs[0].latitude, locs[0].longitude)
    #             doc['pt_location'] = '%s, %s' % (locs[0].latitude, locs[0].longitude)
    #         conn.add([doc])
    #         # print doc

    def _rebuild_index(self, conn):
        """docstring for rebuild_index"""
        
        print "CLEARING INDEX..."
        conn.delete(q='*:*')
        print 'Indexing %s Resources...' % Resource.objects.count()
        for res in Resource.objects:
            res.index(conn)
        
    
    def test_test(self):
        # print 'starting solr test'
        conn = Solr(SOLR_URL)
        
        # self._rebuild_index(conn)
        
        
        ellon = '57.365287, -2.070642'
        peterheid = '57.584806, -1.875630'
        keith = '57.7036280142534, -2.85720247750133'
        loc = keith
        print '\n\n*** keith ', loc
        srch = '"mental health"'
        # search(self, q, **kwargs)
        
        kw = { 'sfield': 'pt_location', 'pt': loc, 'sort': 'geodist() asc', 'fl': '*,score' }
        # kw = { 'fq':'{!geofilt pt=55.8,-3.10 sfield=store d=50}' }

        results = conn.search(srch, **kw)
        print '\n--\nsearch on [%s] : %s' % (srch, loc)
        for result in results:
            print '-', result['res_id'], result['score'], result['title'], result['pt_location']
        
    def test_postcode(self):
        conn = Solr(SOLR_URL)
        
        aberdeen = 'Ab10 1AX'
        # peterheid = '57.584806, -1.875630'
        # keith = '57.7036280142534, -2.85720247750133'
        print '\n\n*** aberdeen', aberdeen
        loc = get_place_for_postcode(aberdeen, DB_NAME)
        print loc
        srch = '"mental health"'
        # search(self, q, **kwargs)
        
        kw = { 'sfield': 'pt_location', 'pt': lat_lon_to_str(loc['lat_lon']), 'sort': 'geodist() asc', 'fl': '*,score' }
        # kw = { 'fq':'{!geofilt pt=55.8,-3.10 sfield=store d=50}' }

        results = conn.search(srch, **kw)
        print '\n--\nsearch on [%s] : %s' % (srch, loc['lat_lon'])
        for result in results:
            print '-', result['score'], result['title'], result['pt_location']
    
    def test_dismax(self):
        """docstring for test_dismax"""

        conn = Solr(SOLR_URL)
        
        kwords = 'citizens advice'
        kw = {
            'rows': settings.SOLR_ROWS,
            'fl': '*,score',
            'qt': 'resources',
        }
        
        results = conn.search(kwords, **kw)

        print '\n--\nsearch on [%s] : ' % (kwords)
        for result in results:
            print '-', result['score'], result['title'] #, result['pt_location']
        
    def test_dismax_loc(self):
        """docstring for test_dismax"""

        conn = Solr(SOLR_URL)

        loc_name = 'downing st'
        loc = TEST_LOCS[loc_name]
        print '\n\n*** %s ' % loc_name, loc
    
        kwords = 'health'
        kw = {
            'rows': settings.SOLR_ROWS,
            'fl': '*,score',
            'qt': 'resources',
            'sfield': 'pt_location',
            'pt': loc,
            'bf': 'recip(geodist(),2,200,20)^2',
            'sort': 'score desc',
        }
    
        results = conn.search(kwords, **kw)

        print '\n--\nsearch on [%s] : ' % (kwords)
        for result in results:
            print '-', result['score'], result['title'], result.get('pt_location', '')
          
#     # def test_form(self):
#     #   """test form creation"""
#     #   uri = 'http://test.example.com/10/'
#     #   title = 'test title'
#     #   form = ShortResourceForm({'uri': uri, 'title': title})
#     #   self.assertTrue(form.is_valid())
    
# class BigResourceTest(TransactionTestCase):
#     
# 
#     def setUp(self):
#         # test for and load big db
#         if Resource.objects.count() == 0:
#             self.db = _load_data('resources')
# 
#     # def test_test(self):
#     #     print 'hello'
# 
#     def test_resources(self):
#         title = u'title 2'
#         url = u'http://test.example.com/2/'
#         self.assertEqual(Resource.objects.count(), 6)
#         resource = Resource.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
#         self.assertEqual(resource.id, u'4d135708e999fb30d8000001')
#         self.assertEqual(resource.item_metadata.author, u'1')
#         # get an resource with a resource with this url
#         # resources could share a url ?
#         # resource = Resource.objects.get(resources__url=url)
#         # self.assertEqual(resource.title, title)

    
    
    
