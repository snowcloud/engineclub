"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Item, Location, get_nearest, load_item_data, update_keyword_index
from depot.forms import ShortItemForm
from mongoengine import connect
from mongoengine.connection import _get_db as get_db

import re


from django.test.simple import *
from django.test import TransactionTestCase

from mongoengine import connect

def _load_data(items='items', locations='locations'):
    """loads fixture data for test Items"""
    item_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, items), 'rU')
    load_item_data('item', item_data)
    item_data.close()
    item_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, locations), 'rU')
    load_item_data('location', item_data)
    item_data.close()
    
class MongoDBTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        db_name = 'test_db'
        connect(db_name)
        print 'Creating test-databasey: ' + db_name
        _load_data()
        return db_name

    def teardown_databases(self, db_name, **kwargs):
        from pymongo import Connection
        conn = Connection()
        conn.drop_database(db_name)
        print 'Dropping test-databasey: ' + db_name


class ItemTest(TransactionTestCase):
    
        
    def setUp(self):
        if Item.objects.count() == 0:
            self.db = _load_data()

    def tearDown(self):
        Item.drop_collection()
        Location.drop_collection()
    
    def test_items(self):
        title = u'title 2'
        url = u'http://test.example.com/2/'
        self.assertEqual(Item.objects.count(), 6)
        item = Item.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
        self.assertEqual(item.id, u'4d135708e999fb30d8000001')
        self.assertEqual(item.metadata.author, u'1')
        # get an item with a resource with this url
        # items could share a url ?
        item = Item.objects.get(resources__url=url)
        self.assertEqual(item.title, title)
        
    def test_newitem(self):
        """
        Tests create a new item.
        """
        # uri = u'http://test.example.com/1/'
        title = u'test title 7'
        author = u"1"
        item, created = Item.objects.get_or_create(__raw__={'_id': u'4d135708e999fb30d8000007'}, defaults={'title': title})
        item.metadata.author = author
        self.assertTrue(created)
        # self.assertEqual(unicode(item.id), u'4d135708e999fb30d8000001')
        self.assertEqual(item.title, title)
        self.assertEqual(item.metadata.author, author)
    
    def test_tags(self):
        """docstring for test_tags"""
        # self._load_data()
        items = Item.objects(tags='red')
        # print [(i.title, i.tags) for i in Item.objects]
        # print 'red items: ', items
        self.assertEqual(len(items), 3)
        # 6 tags contain blue OR red
        items = Item.objects(tags__in=['blue', 'red'])
        self.assertEqual(len(items), 6)
        # 2 tags contain blue AND red
        items = Item.objects(tags__all=['blue', 'red'])
        self.assertEqual(len(items), 2)
    
    def test_tagslist(self):
        """docstring for test_tagslist"""
        # self.db = self._load_data()
        for item in Item.objects:
            item.make_keys([])
            item.save()
        update_keyword_index()
        results = get_db().keyword.find( { "_id" : re.compile('^Bl*', re.IGNORECASE)} ) #.count()
        self.assertEqual([i['_id'] for i in results], [u'blue'])
      
    def test_geo(self):
        """docstring for test_geo"""
        # db = self._load_data()
        for item in Item.objects:
            item.make_keys([])
            item.save()
        update_keyword_index()
        results = get_nearest('50', -3.00, categories=['blue']) # takes float or string for lat, lon
        #       print results
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]['items']), 2)
      
    # def test_form(self):
    #   """test form creation"""
    #   uri = 'http://test.example.com/10/'
    #   title = 'test title'
    #   form = ShortItemForm({'uri': uri, 'title': title})
    #   self.assertTrue(form.is_valid())
    
class BigItemTest(TransactionTestCase):
    

    def setUp(self):
        # test for and load big db
        if Item.objects.count() == 0:
            self.db = _load_data('items')

    def test_test(self):
        print 'hello'

    def test_items(self):
        title = u'title 2'
        url = u'http://test.example.com/2/'
        self.assertEqual(Item.objects.count(), 6)
        item = Item.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
        self.assertEqual(item.id, u'4d135708e999fb30d8000001')
        self.assertEqual(item.metadata.author, u'1')
        # get an item with a resource with this url
        # items could share a url ?
        item = Item.objects.get(resources__url=url)
        self.assertEqual(item.title, title)

    
    
    
