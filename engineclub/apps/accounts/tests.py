# -*- coding: utf-8 -*-
"""
engine-groups/tests.py
"""

import subprocess

from django.contrib.auth.models import User
from mongoengine.connection import _get_db as get_db
from mongoengine.django.tests import MongoTestCase

from depot.models import Resource
from accounts.models import Account, Collection, Membership, \
    MEMBER_ROLE, ADMIN_ROLE

SEP = '**************'

# import json
# from mongoengine import base as mongobase
# from pymongo import json_util

def _dump_collections(collection_names=None):
    if collection_names is None:
        collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
    for coll in collection_names:
        subprocess.call([
            'mongoexport', 
            '-d', '%s' % get_db().name, 
            '-c', '%s' % coll, 
            '-o', 'output_%s.json' % coll])

def _load_collections(collection_names=None, drop='--drop'):
    if collection_names is None:
        collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
    for coll in collection_names:
        subprocess.call([
            'mongoimport', 
            '-d', '%s' % get_db().name, 
            '-c', '%s' % coll, 
            '--file', 'output_%s.json' % coll, 
            '%s' % drop])

def _print_db_info():
    """docstring for _print_db_info"""
    print SEP
    print 'Account: ', Account.objects.count()
    print 'Membership: ', Membership.objects.count()
    print 'Collection: ', Collection.objects.count()
    print SEP

def _make_user(name):
    return User.objects.create_user(name, email="%s@example.com" % name, password='password')

class AccountsBaseTest(MongoTestCase):
    def setUp(self):
        # _print_db_info()
        self.user_bob = _make_user('bob')
        self.user_humph = _make_user('humph')
        self.user_jorph = _make_user('jorph')
        self.user_group = _make_user('group')

        self.bob = Account.objects.create(name="Bob Hope", email="bob@example.com", local_id=str(self.user_bob.id))
        self.humph = Account.objects.create(name="Humph Floogerwhippel", email="humph@example.com", local_id=str(self.user_humph.id))
        self.jorph = Account.objects.create(name="Jorph Wheedjilli", email="jorph@example.com", local_id=str(self.user_jorph.id))
        self.group = Account.objects.create(
            name="Flupping Baxters of Falkirk", 
            email="group@example.com", 
            local_id=str(self.user_group.id),
            )
        self.group.add_member(self.humph)
        self.group.add_member(self.jorph, role=ADMIN_ROLE)

    def tearDown(self):
        # _print_db_info()
        pass

class CollectionsTest(AccountsBaseTest):

    def test_creation(self):

        coll1 = Collection.objects.create(name='Test Collection', owner=self.bob)
        coll2 = Collection.objects.create(name='Test Collection 2', owner=self.humph)
        self.assertEqual(1, Collection.objects(owner=self.bob).count())

        coll1.add_accounts([self.humph, self.jorph])
        coll1.add_accounts([self.humph])
        coll1.add_accounts([self.jorph])
        self.assertEqual(2, len(coll1.accounts))

        self.assertEqual(1, len(self.humph.collections))
        self.assertEqual(self.humph.collections[0].name, 'Test Collection')

        coll2.add_accounts([self.jorph])
        self.assertEqual(1, len(coll2.accounts))

        self.assertEqual(2, len(self.jorph.collections))

class AccountsTest(AccountsBaseTest):
    def test_account(self):
        self.assertEqual(Account.objects.count(), 4)
        _dump_collections()

    def test_load_accounts(self):
        """docstring for test_load_accounts"""
        _load_collections()
        self.assertEqual(Account.objects.count(), 4)

        arthur = _make_user('arthur')
        acct1 = Account.objects.create(name="Arthur Sixpence", email="arthur@example.com", local_id=str(arthur.id))

        self.group.add_member(acct1)
        self.group.save()
        self.assertEqual(len(self.group.members), 3)

        
        
        
        