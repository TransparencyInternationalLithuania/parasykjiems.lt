#!/usr/bin/python
# This Python file uses the following encoding: utf-8

from django.test import TestCase
import unittest
from django.test.client import Client
import os, sys

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        test_addresses = [
            'Žygio 90, Vilnius',
            'Žvejų 16, Antanašė, Rokiškio raj.',
            'Mindaugo 16, Kaunas',
            'Antanašė, Rokiškio raj.',
        ]
        for test in test_addresses:
            response = self.client.post('/pjweb/', {'address':test})

            response = self.client.get('/pjweb/')

            # Check that the response is 200 OK.
            ok = self.failUnlessEqual(response.status_code, 200)
