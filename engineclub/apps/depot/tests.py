# -*- coding: utf-8 -*-
"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Resource, Location, get_nearest, load_resource_data, update_keyword_index
from depot.forms import ShortResourceForm
from mongoengine import connect
from mongoengine.connection import _get_db as get_db

import re


from django.test.simple import *
from django.test import TransactionTestCase

from mongoengine import connect
TEST_DB_NAME = 'test_db2'

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
    resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, locations), 'rU')
    load_resource_data('location', resource_data)
    resource_data.close()
    
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
      
    def test_test(self):
        print 'starting solr test'
        conn = Solr(settings.SOLR_URL)
        conn.delete(q='*:*')

        # docs = [
        #     {'id': 'testdoc.1', 'title': 'document 1', 'text': u'Paul Verlaine'},
        #     {'id': 'testdoc.2', 'title': 'document 2', 'text': u'Giffer Владимир'},
        #     ]
        
        conn.add([{'id': r.id, 'title': r.title, 'text': r.description, 'keywords': r.index_keys} for r in Resource.objects])
        srch = 'yellow'
        results = conn.search(srch)
        print 'search on \'%s\'' % srch
        for result in results:
            print result
        
        print
          
          
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

    
    
    
