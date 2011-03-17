from django.test.client import Client
from django.test.testcases import TestCase

class TestUserEntersAddress(TestCase):
    fixtures = ['territoryPlugin/single street.json']

    def test_SubmitEmpty(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        c = Client()
        c.post('/pjweb/', {"address_input" : u"" })

    def test_SubmitDirectHit(self):
        """ User enters an address, and WTT redirects to a page where members are displayed.
        This is a direct hit, and page should redirect to representative page
        In this test no representatives are displayed. The goal is to test that no import errors occur"""
        c = Client()
        resp = c.post('/pjweb/', {"address_input" : u"Gedimino 9" })

        # a redirect is generated
        self.assertEqual("", resp.content)
        self.assertEqual(302, resp.status_code)

class TestDisplayMembersFromStreet(TestCase):
    def test_randomPage(self):
        """Asking to show members for an unknown / random place. Should not fail with imports"""
        c = Client()
        resp = c.get('/pjweb/choose_rep/random/random/random/9/')

        # just check that response was generated
        self.assertEqual(True, resp.content != "")
        self.assertEqual(200, resp.status_code)


