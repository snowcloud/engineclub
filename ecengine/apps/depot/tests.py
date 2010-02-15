"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from apps.depot.models import Item, load_item_data
from apps.depot.forms import ItemForm
from mongoengine import connect

ITEM_COLLECTION = 'test_items'

class ItemTest(TestCase):
    
    def setUp(self):
        connect('test_db', host='localhost', port=27017)
        # self._load_data()
        
    def tearDown(self):
        # for item in Item.objects:
        #     print item.id, item.name
        Item.drop_collection()

    #     
    # def test_collection(self):
    #     """docstring for test_collection"""
    #     self.failUnlessEqual(self.itemcoll.count(), 1)
        
    def test_items(self):
        item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
        load_item_data(item_data)
        item_data.close()
        self.assertEqual(Item.objects.count(), 6)
        
    def test_newitem(self):
        """
        Tests create a new item.
        """
        item = Item.objects.get_or_create(name='fred', defaults={})
        self.assertEqual(item.name, 'fred')
        
        
    def test_form(self):
        """test form creation"""
        # item = Item()
        # item.name = 'fred'
        form = ItemForm({'name': 'joe'})
        self.assertTrue(form.is_valid())

