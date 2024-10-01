# cyberapps.commerce.order

""" Order and order item classes.
"""

from zope.app.intid.interfaces import IIntIds
from zope.cachedescriptors.property import Lazy
from zope import component
from zope.component import adapts
from zope.interface import implementer, Interface

from cyberapps.commerce.interfaces import IOrder
from cybertools.commerce.order import Order as BaseOrder
from cybertools.commerce.order import OrderItem as BaseOrderItem
from cybertools.commerce.order import OrderItems as BaseOrderItems
from loops.common import AdapterBase, ParentRelation
from loops.interfaces import ILoopsObject
from loops import util
from loops.type import TypeInterfaceSourceList


TypeInterfaceSourceList.typeInterfaces += (IOrder,)


@implementer(IOrder)
class Order(AdapterBase, BaseOrder):

    _adapterAttributes = ('context', '__parent__', 'customer')
    _contextAttributes = list(IOrder)

    #shop = ParentRelation('shop.order')    # implemented as context attribute
    customer = ParentRelation('customer.order')


class OrderItem(BaseOrderItem):

    def getObject(self, ref):
        if isinstance(ref, int):
            return util.getObjectForUid(ref)
        if isinstance(ref, basestring):
            if ref.isdigit:
                return util.getObjectForUid(ref)
            if ':' in ref:
                tp, id = ref.split(':', 1)
                return (tp, id)
        return ref


class OrderItems(BaseOrderItems):

    # utility methods

    def getUid(self, obj):
        if ILoopsObject.providedBy(obj):
            return util.getUidForObject(obj, self.intIds)
        elif isinstance(obj, AdapterBase):
            return util.getUidForObject(obj.context, self.intIds)
        return obj

