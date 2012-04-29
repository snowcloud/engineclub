# -*- coding: utf-8 -*-
"""
engine-groups/tests.py
"""

# import subprocess

from django.contrib.auth.models import User
from mongoengine.connection import _get_db as get_db
from ecutils.tests import MongoTestCase

# from resources.models import Resource
from accounts.models import Account, Collection, \
    MEMBER_ROLE, ADMIN_ROLE

SEP = '**************'

# def _dump_collections(collection_names=None):
#     if collection_names is None:
#         collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
#     for coll in collection_names:
#         subprocess.call([
#             'mongoexport', 
#             '-d', '%s' % get_db().name, 
#             '-c', '%s' % coll, 
#             '-o', 'output_%s.json' % coll])

# def _load_collections(collection_names=None, drop='--drop'):
#     if collection_names is None:
#         collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
#     for coll in collection_names:
#         subprocess.call([
#             'mongoimport', 
#             '-d', '%s' % get_db().name, 
#             '-c', '%s' % coll, 
#             '--file', 'output_%s.json' % coll, 
#             '%s' % drop])

# def _print_db_info():
#     """docstring for _print_db_info"""
#     print SEP
#     print 'Account: ', Account.objects.count()
#     # print 'Membership: ', Membership.objects.count()
#     print 'Collection: ', Collection.objects.count()
#     print SEP

def make_test_user_and_account(name):
    user = User.objects.create_user(name, email="%s@example.com" % name, password='password')
    acct = Account.objects.create(
        name=name, 
        email="%s@example.com" % name,
        description="%s's account." % name,
        local_id=str(user.id))
    return user, acct

def setUpAccounts(self):

        # Create normal contrib.auth users & their mongodb accounts
        for name in ['alice', 'bob', 'emma', 'hugo', 'jorph','group']:
            a, b =  make_test_user_and_account(name)
            setattr(self, 'user_%s' % name, a)
            setattr(self, name, b)

        # Add alice to the group, so she is a "sub account"
        # self.group.add_member(self.alice)
        # self.group.add_member(self.jorph, role=ADMIN_ROLE)

class AccountsBaseTest(MongoTestCase):

    def setUp(self):
        setUpAccounts(self)

class CollectionsTest(AccountsBaseTest):

    def test_creation(self):
        coll1 = Collection.objects.create(name='Test Collection', owner=self.bob)
        coll2 = Collection.objects.create(name='Test Collection 2', owner=self.alice)
        self.assertEqual(1, Collection.objects(owner=self.bob).count())

        coll1.add_accounts([self.alice, self.jorph])
        coll1.add_accounts([self.alice])
        coll1.add_accounts([self.jorph])
        coll1.save()
        coll1 = Collection.objects.get(name='Test Collection')
        self.assertEqual(2, len(coll1.accounts))

        self.assertEqual(1, len(self.alice.in_collections))
        self.assertEqual(self.alice.in_collections[0].name, 'Test Collection')

        coll2.add_accounts([self.jorph])
        coll2.save()
        self.jorph.save()
        self.assertEqual(1, len(coll2.accounts))

        self.assertEqual(2, len(self.jorph.in_collections))

class AccountsTest(AccountsBaseTest):

    def test_load_accounts(self):
        """docstring for test_load_accounts"""
        # _load_collections()
        self.assertEqual(Account.objects.count(), 6)

        arthur, acct1 = make_test_user_and_account('arthur')
        # acct1 = Account.objects.create(name="Arthur Sixpence", email="arthur@example.com", local_id=str(arthur.id))

        self.group.add_member(acct1)
        self.group.save()
        self.assertEqual(len(self.group.members), 1)

        
        
        
        