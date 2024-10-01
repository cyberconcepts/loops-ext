# cyberapps.commerce.shop

""" Shop adapter.
"""

from zope.interface import implementer
from zope.traversing.api import getName

from cyberapps.commerce.interfaces import IShop
from cybertools.commerce.shop import Shop as BaseShop
from loops.common import AdapterBase, ChildRelationSetProperty
from loops.type import TypeInterfaceSourceList


TypeInterfaceSourceList.typeInterfaces += (IShop,)


@implementer(IShop)
class Shop(AdapterBase, BaseShop):

    _adapterAttributes = ('context', '__parent__',
                          'products', 'categories', 'suppliers', 'customers')
    _contextAttributes = list(IShop)
    _noexportAttributes = ('products', 'customers')

    products = ChildRelationSetProperty('shop.product')
    customers = ChildRelationSetProperty('shop.customer')

    @property
    def name(self):
        return getName(self.context)
