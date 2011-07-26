"""Tests for 'parasykjiems.web'.

By default, Django only looks for tests in an app's models and tests
modules. We want to put doctests in all modules, so we override the
suite() function here and list the modules we want to test in
TEST_MODULES.
"""

import unittest
import doctest


# Modules to load tests from.
TEST_MODULES = (
    'web.multisub',
    'web.lang',
    'web.house_numbers',
)


def suite():
    suite = unittest.TestSuite()
    for t in TEST_MODULES:
        try:
            suite.addTest(doctest.DocTestSuite(
                __import__(t, globals(), locals(), fromlist=["*"])
            ))
        except ValueError:
            # If a module doesn't contain any doctests, we simply ignore it.
            pass

        suite.addTest(unittest.TestLoader().loadTestsFromModule(
            __import__(t, globals(), locals(), fromlist=["*"])
        ))

    return suite
