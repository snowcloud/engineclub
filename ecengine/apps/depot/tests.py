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
        

