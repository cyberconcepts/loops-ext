# cyberapps.commerce.manager

""" The commerce manager (container, registry, ...).
"""

from zope.cachedescriptors.property import Lazy
from zope.component import adapts
from zope.interface import implementer

from cybertools.commerce.interfaces import IManager, IOrderItems
from loops.common import TypeInstancesProperty
from loops.concept import Concept
from loops.interfaces import IConceptManager
from loops.setup import addAndConfigureObject


@implementer(IManager)
class Manager(object):

    adapts(IConceptManager)

    langInfo = None

    shops = TypeInstancesProperty('shop')
    products = TypeInstancesProperty('product', 'productId', 'p')
    categories = TypeInstancesProperty('category', 'name', 'cat')
    customers = TypeInstancesProperty('customer', 'customerId', 'c',
                                      container='customers')
    orders = TypeInstancesProperty('order', 'orderId', '',
                                      container='orders')

    def __init__(self, context):
        self.context = context

    @Lazy
    def records(self):
        return self.context.getLoopsRoot().getRecordManager()

    @Lazy
    def orderItems(self):
        return IOrderItems(self.records['orderitems'])

