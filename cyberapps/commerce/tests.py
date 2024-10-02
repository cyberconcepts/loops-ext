# cyberapps.commerce.tests

import unittest, doctest
from zope.testing.doctestunit import DocFileSuite
from zope import component
from zope.interface.verify import verifyClass

from cyberapps.commerce.customer import Customer, Address
from cyberapps.commerce.interfaces import IShop, IProduct, ICategory
from cyberapps.commerce.interfaces import ICustomer, IAddress, IOrder
from cyberapps.commerce.order import Order, OrderItems
from cyberapps.commerce.product import Product, Category
from cyberapps.commerce.shop import Shop
from cyberapps.commerce.setup import SetupManager
from cybertools.commerce.interfaces import IProduct
from loops.interfaces import ILoops
from loops.setup import ISetupManager
from loops.tests.setup import TestSite as BaseTestSite


class TestSite(BaseTestSite):

    def __init__(self, site):
        self.site = site

    def setup(self):
        component.provideAdapter(SetupManager, (ILoops,), ISetupManager,
                         name='cyberapps.commerce')
        component.provideAdapter(Shop, provides=IShop)
        component.provideAdapter(Product, provides=IProduct)
        component.provideAdapter(Category, provides=ICategory)
        component.provideAdapter(Customer, provides=ICustomer)
        component.provideAdapter(Address, provides=IAddress)
        component.provideAdapter(Order, provides=IOrder)
        component.provideAdapter(OrderItems)
        concepts, resources, views = self.baseSetup()
        return concepts, resources, views


class Test(unittest.TestCase):
    "Basic tests for the cyberapps.commerce package."

    def testSomething(self):
        pass


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.TestLoader().loadTestsFromTestCase(Test),
        DocFileSuite('README.txt', optionflags=flags),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
