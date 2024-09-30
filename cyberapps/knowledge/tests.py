# cyberapps.knowledge.tests

import os
import unittest, doctest
from zope.interface.verify import verifyClass

from loops.setup import importData as baseImportData


importPath = os.path.dirname(__file__)


def importData(loopsRoot):
    baseImportData(loopsRoot, importPath, 'knowledge_de.dmp')


class Test(unittest.TestCase):
    "Basic tests for the cyberapps.knowledge package."

    def testSomething(self):
        pass


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
                unittest.makeSuite(Test),
                doctest.DocFileSuite('README.txt', optionflags=flags),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
