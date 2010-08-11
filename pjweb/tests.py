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
            '',
        ]
        for test in test_addresses:
            print test
            response = self.client.post('/pjweb/', {'address':test})
            # Check that the response is 200 OK.
            ok = self.failUnlessEqual(response.status_code, 200)
