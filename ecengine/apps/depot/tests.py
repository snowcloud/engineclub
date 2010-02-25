"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Item, load_item_data
from depot.forms import ItemForm
from mongoengine import connect

# *******   WARNING  *********
# mongoengine.connect not resetting the db, so tearDown is clearing main DB

class ItemTest(TestCase):
    
    def setUp(self):
        if not settings.MONGO_TESTING:
            raise Exception('must use settings_testing for these tests')
        connect('test_db', host='localhost', port=27017)
        
    def tearDown(self):
        Item.drop_collection()

    def test_items(self):
        item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
        load_item_data(item_data)
        item_data.close()
        self.assertEqual(Item.objects.count(), 6)
        
    def test_newitem(self):
        """
        Tests create a new item.
        """
        url = 'http://test.example.com/1/'
        title = 'test title'
        item = Item.objects.get_or_create(url=url, defaults={'title': title})
        self.assertEqual(item.url, url)
        self.assertEqual(item.title, title)
        
        
    def test_form(self):
        """test form creation"""
        url = 'http://test.example.com/10/'
        title = 'test title'
        form = ItemForm({'url': url, 'title': title})
        self.assertTrue(form.is_valid())

