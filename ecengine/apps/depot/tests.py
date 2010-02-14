"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from apps.depot.models import TestItem
from apps.depot.forms import ItemForm

class ItemTest(TestCase):
    def test_newitem(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        item = TestItem()
        item.name = 'fred'
        item.save()
        self.failUnlessEqual(item.name, 'fred')
        
    def test_form(self):
        """docstring for test_form"""
        item = TestItem()
        item.name = 'fred'
        form = ItemForm({'name': 'joe'}, instance=item)
        i = form.save(commit=False)
        # 
        print i
        print form.is_valid()
        print form
        

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


# # from django.db import models
# 
# # Create your models here.
# 
# 
# from django.core.management import setup_environ
# 
# import sys, os
# sys.path.append('/Users/derek/dev_django')
# sys.path.append('/Users/derek/dev_django/shared_apps')
# 
# from ecengine import settings
# 
# setup_environ(settings)
# 
# from django.db import models
# 
# class TestItem(models.Model):
# 
#     name = models.CharField(blank=True, max_length=80)
#     
#     # class Meta:
#     #     abstract = True
# 
# # from smgclasses.models import SMGClass
# print 'blah'
# 


