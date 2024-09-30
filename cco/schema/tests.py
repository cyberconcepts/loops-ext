#! /usr/bin/python

"""
Tests for the 'cco.schema' package.
"""

import os
import unittest, doctest
from zope import component
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.publisher.browser import TestRequest

from cco.schema.base import SchemaController
from cco.schema.interfaces import ISchemaController
from cco.schema.processor import SchemaProcessor
from loops.setup import importData as baseImportData
from loops.tests.setup import TestSite


def setUp(self):
    site = placefulSetUp(True)
    t = TestSite(site)
    concepts, resources, views = t.setup()
    loopsRoot = site['loops']
    self.globs['loopsRoot'] = loopsRoot


def tearDown(self):
    placefulTearDown()


importPath = os.path.join(os.path.dirname(__file__), 'data')

def importData(loopsRoot):
    component.provideAdapter(SchemaController)
    component.provideAdapter(SchemaProcessor)
    baseImportData(loopsRoot, importPath, 'cco_schema_en.dmp')


class Test(unittest.TestCase):
    "Basic tests."

    def testBasicStuff(self):
        pass


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        doctest.DocFileSuite('README.md', optionflags=flags,
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
