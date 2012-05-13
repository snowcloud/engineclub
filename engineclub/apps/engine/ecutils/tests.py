"""
ecutils.tests
"""

from django.test import TestCase
from django.conf import settings

class SimpleTest(TestCase):
    def test_utils_minmax(self):

    	from ecutils.utils import minmax

    	self.assertEqual(2, minmax(-2, 9000, 2))
    	self.assertEqual(-2, minmax(-2, 9000, -3))
    	self.assertEqual(9000, minmax(-2, 9000, 9000))
    	self.assertEqual(9000, minmax(-2, 9000, 9001))
    	self.assertEqual(90, minmax(80, 9000, None, default=90))
    	self.assertEqual(9000, minmax(80, 9000, None, default=9001))
    	self.assertEqual(80, minmax(80, 9000, None, default=-18))


from mongoengine import connect, connection

class MongoTestCase(TestCase):
    """
    TestCase class that clear the collection between the tests
    """
    db_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    def __init__(self, methodName='runtest'):
        connection.disconnect()
        self.db = connect(self.db_name)
        super(MongoTestCase, self).__init__(methodName)

    def _post_teardown(self):
        super(MongoTestCase, self)._post_teardown()
        for collection in connection.get_db().collection_names():
            if collection == 'system.indexes':
                continue
            connection.get_db().drop_collection(collection)

class SettingTest(MongoTestCase):
    """docstring for SettingTest"""

    def test_setting(self):
        from models import Setting

        TESTKEY = 'test'
        TESTVALUE = 'wabbit'
        TESTVALUE_DICT = {'one': 'potato', 'two': 'potatoes'}

        setting, created = Setting.objects.get_or_create(key=TESTKEY)
        self.assertTrue(created)
        setting.value['data'] = TESTVALUE
        setting.save()

        setting.reload()
        self.assertEqual(setting.value['data'], TESTVALUE)

        setting.value['data'] = TESTVALUE_DICT
        setting.save()

        setting.reload()
        self.assertEqual(setting.value['data'], TESTVALUE_DICT)
