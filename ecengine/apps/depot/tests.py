"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Item, load_item_data
from depot.forms import ShortItemForm
from mongoengine import connect, Q

# *******   WARNING  *********
# mongoengine.connect not resetting the db, so tearDown is clearing main DB
# unless settings_test used

class ItemTest(TestCase):
    
    def setUp(self):
        if not settings.MONGO_TESTING:
            raise Exception('must use ecengine.settings_test for these tests')
        connect('test_db', host='localhost', port=27017)
        
    def tearDown(self):
        Item.drop_collection()

    def _load_item_data(self):
        """docstring for _load_item_data"""
        item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
        load_item_data(item_data)
        item_data.close()

    def test_items(self):
        self._load_item_data()
        self.assertEqual(Item.objects.count(), 6)
        item = Item.objects.get(url='http://test.example.com/1/')
        self.assertEqual(item.url, 'http://test.example.com/1/')
        self.assertEqual(item.metadata.author, '1')
        
    def test_newitem(self):
        """
        Tests create a new item.
        """
        url = 'http://test.example.com/1/'
        title = 'test title'
        author = "1"
        item = Item.objects.get_or_create(url=url, defaults={'title': title})
        item.metadata.author = author
        self.assertEqual(item.url, url)
        self.assertEqual(item.title, title)
        self.assertEqual(item.metadata.author, author)
    
    def test_tags(self):
        """docstring for test_tags"""
        self._load_item_data()
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

    def test_form(self):
        """test form creation"""
        url = 'http://test.example.com/10/'
        title = 'test title'
        form = ShortItemForm({'url': url, 'title': title})
        self.assertTrue(form.is_valid())

