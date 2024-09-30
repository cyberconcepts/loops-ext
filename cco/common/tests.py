#! /usr/bin/python

"""
Tests for the 'cco.webapi' package.
"""

import io
import logging
import os
import sys
import unittest, doctest
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope import component
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

from loops.interfaces import IConceptSchema, ITypeConcept
from loops.setup import importData as baseImportData
from loops.tests.setup import TestSite


class LogHandler(logging.StreamHandler):

    def emit(self, record):
        print('%s: %s' % (record.levelname, record.msg))

logger = logging.getLogger('cco.common')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.addHandler(LogHandler())


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
        unittest.makeSuite(Test),
        doctest.DocFileSuite('README.rst', optionflags=flags,
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
