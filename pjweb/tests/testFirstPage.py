from django.test.client import Client
from django.test.testcases import TestCase

class TestFirstPage(TestCase):
    def test_single_range_odd(self):
        """ Just open first page. Should not get any import errrors"""
        c = Client()
        c.get('/')

