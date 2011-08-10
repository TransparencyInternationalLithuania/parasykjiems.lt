from django.test.client import Client
from django.test.testcases import TestCase
from pjweb.email.emailTemplates import renderEmailTemplate
from settings import GlobalSettings

class TestRenderAllEmailTemplates_InEveryLanguage(TestCase):
    def test_email_confirmation(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        for lang in GlobalSettings.LANGUAGES:
            l = u"%s" % (lang[0])
            renderEmailTemplate("email_confirmation.txt", {}, lang = l)

    def test_email_to_representative(self):
        """ User enters an address, and WTT returns a normal response, no import errors"""
        for lang in GlobalSettings.LANGUAGES:
            l = u"%s" % (lang[0])
            renderEmailTemplate("email_to_representative.txt", {}, lang = l)




