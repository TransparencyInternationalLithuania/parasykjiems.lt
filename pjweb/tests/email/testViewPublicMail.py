from django.test.client import Client
from django.test.testcases import TestCase

class TestViewMailList(TestCase):
    def test_tryToViewNonExistentEmail(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        c = Client()
        resp = c.get('/public/9999999/')

        # a redirect is generated
        self.assertEqual(404, resp.status_code)
        #self.assertEqual("", resp.content)
