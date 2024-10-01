# cyberapps.commerce.customer

""" Customer adapter and related classes.
"""

from zope.interface import implementer

from cyberapps.commerce.interfaces import ICustomer, IAddress
from cybertools.commerce.customer import Customer as BaseCustomer
from cybertools.commerce.customer import Address as BaseAddress
from loops.common import AdapterBase
from loops.common import ChildRelationSetProperty, ParentRelationSetProperty
from loops.interfaces import IConceptSchema
from loops.type import TypeInterfaceSourceList


TypeInterfaceSourceList.typeInterfaces += (ICustomer, IAddress)


@implementer(ICustomer)
class Customer(AdapterBase, BaseCustomer):

    _adapterAttributes = ('context', '__parent__', 'shops')
    _contextAttributes = list(ICustomer)
    _noexportAttributes = ('shops', 'orders')

    shops = ParentRelationSetProperty('shop.customer', noSecurityCheck=True)
    orders = ChildRelationSetProperty('customer.order')

    @property
    def identifier(self):
        return self.customerId


@implementer(IAddress)
class Address(AdapterBase, BaseAddress):

    _contextAttributes = list(IAddress)

