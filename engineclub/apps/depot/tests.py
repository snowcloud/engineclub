"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Item, Location, get_nearest, load_item_data, update_keyword_index
from depot.forms import ShortItemForm
from mongoengine import connect

import re


class ItemTest(TestCase):
    
    def setUp(self):
        connect('test_db', host='localhost', port=27017)
        
    def tearDown(self):
        Item.drop_collection()
        Location.drop_collection()

    def _load_data(self):
        """loads fixture data for test Items"""
        item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
        load_item_data('item', item_data)
        item_data.close()
        item_data = open('%s/apps/depot/fixtures/locations.json' % settings.PROJECT_PATH, 'rU')
        db = load_item_data('location', item_data)
        item_data.close()
        return db

    def test_items(self):
        self._load_data()
        self.assertEqual(Item.objects.count(), 6)
        item = Item.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
        self.assertEqual(item.id, u'4d135708e999fb30d8000001')
        self.assertEqual(item.metadata.author, u'1')
        
    def test_newitem(self):
      """
      Tests create a new item.
      """
      # uri = u'http://test.example.com/1/'
      title = u'test title'
      author = u"1"
      item, created = Item.objects.get_or_create(__raw__={'_id': u'4d135708e999fb30d8000001'}, defaults={'title': title})
      item.metadata.author = author
      self.assertTrue(created)
      # self.assertEqual(unicode(item.id), u'4d135708e999fb30d8000001')
      self.assertEqual(item.title, title)
      self.assertEqual(item.metadata.author, author)
    
    def test_tags(self):
      """docstring for test_tags"""
      self._load_data()
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
      db = self._load_data()
      for item in Item.objects:
          item.make_keys([])
          item.save()
      update_keyword_index()
      results = db.keyword.find( { "_id" : re.compile('^Bl*', re.IGNORECASE)} ) #.count()
      self.assertEqual([i['_id'] for i in results], [u'blue'])
      
    def test_geo(self):
      """docstring for test_geo"""
      db = self._load_data()
      for item in Item.objects:
          item.make_keys([])
          item.save()
      update_keyword_index()
      results = get_nearest('50', -3.00, categories=['blue']) # takes float or string for lat, lon
#       print results
      self.assertEqual(len(results), 1)
      self.assertEqual(len(results[0]['items']), 2)
      
#     def test_form(self):
#       """test form creation"""
#       uri = 'http://test.example.com/10/'
#       title = 'test title'
#       form = ShortItemForm({'uri': uri, 'title': title})
#       self.assertTrue(form.is_valid())

