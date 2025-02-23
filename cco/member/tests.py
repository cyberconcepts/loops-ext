# cco.member.tests

""" Tests for the 'cco.member' package.
"""

import os
import unittest, doctest
from zope import component
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.publisher.browser import TestRequest

from loops.interfaces import IConceptManager
from loops.tests.setup import TestSite


def setUp(self):
    site = placefulSetUp(True)
    t = TestSite(site)
    concepts, resources, views = t.setup()
    loopsRoot = site['loops']
    self.globs['loopsRoot'] = loopsRoot


def tearDown(self):
    placefulTearDown()


class Test(unittest.TestCase):
    "Basic tests."

    def testBasicStuff(self):
        pass


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.TestLoader().loadTestsFromTestCase(Test),
        doctest.DocFileSuite('README.txt', optionflags=flags,
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
