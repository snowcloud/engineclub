"""
ecutils.tests
"""

from django.test import TestCase

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

