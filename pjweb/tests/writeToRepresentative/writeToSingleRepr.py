from django.test.client import Client
from django.test.testcases import TestCase

class TestWriteToSingleRepr(TestCase):
    fixtures = ['writeToRepresentative/representative with email.json']

    def test_SubmitNonExistentMember(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        c = Client()
        resp = c.get('/contact/mayor/9999999/')

        # a redirect is generated
        self.assertEqual("", resp.content)
        self.assertEqual(302, resp.status_code)

    def test_ShowExistentMember(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        c = Client()
        resp = c.get('/contact/mayor/1/')

        self.assertEqual(200, resp.status_code)

    def test_ExistentMember_SubmitForPreview(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        c = Client()
        resp = c.post('/contact/mayor/1/', {'sender_name': 'my name', 'message' : 'my message to representative', 'sender':'myEmail@gmail.com', 'public' : 'public'} )

        self.assertEqual(200, resp.status_code)

class TestWriteToSingleRepr_NoEmail(TestCase):
    fixtures = ['writeToRepresentative/representative with no email.json']

    def test_SubmitExistentMember_NoEmail(self):
        c = Client()
        resp = c.get('/contact/mayor/1/')

        # redirect to a page with No Email
        self.assertEqual("", resp.content)
        self.assertEqual(302, resp.status_code)

    def test_no_email_redirect(self):
        c = Client()
        resp = c.get('/contact/mayor/1/no_email/')

        # redirect to a page with No Email
        self.assertEqual(200, resp.status_code)