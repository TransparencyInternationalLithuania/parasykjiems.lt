import unittest
import doctest


# Modules to load tests from.
TEST_MODULES = (
    'web.multisub',
    'web.lang',
)


def suite():
    suite = unittest.TestSuite()
    for t in TEST_MODULES:
        suite.addTest(doctest.DocTestSuite(
            __import__(t, globals(), locals(), fromlist=["*"])
        ))
        suite.addTest(unittest.TestLoader().loadTestsFromModule(
            __import__(t, globals(), locals(), fromlist=["*"])
        ))
    return suite
