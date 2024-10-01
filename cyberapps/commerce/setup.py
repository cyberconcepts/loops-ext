# cyberapps.commerce.setup

""" Automatic setup of a loops site for the commerce package.
"""

from zope.component import adapts

from cyberapps.commerce.order import OrderItem
from cybertools.commerce.interfaces import IShop, IProduct, ICategory
from cybertools.commerce.interfaces import ICustomer, IOrder
from cybertools.tracking.btree import TrackingStorage
from loops.concept import Concept, ConceptManager
from loops.interfaces import ITypeConcept
from loops.setup import SetupManager as BaseSetupManager


class SetupManager(BaseSetupManager):

    def setup(self):
        concepts = self.context.getConceptManager()
        type = concepts.getTypeConcept()
        predicate = concepts.getPredicateType()
        customers = self.addObject(self.context, ConceptManager, 'customers')
        orders = self.addObject(self.context, ConceptManager, 'orders')
        # type concepts:
        tShop = self.addAndConfigureObject(concepts, Concept, 'shop',
                        title=u'Shop', conceptType=type, typeInterface=IShop)
        tProduct = self.addAndConfigureObject(concepts, Concept, 'product',
                        title=u'Product', conceptType=type, typeInterface=IProduct)
        tCategory = self.addAndConfigureObject(concepts, Concept, 'category',
                        title=u'Category', conceptType=type, typeInterface=ICategory)
        tCustomer = self.addAndConfigureObject(concepts, Concept, 'customer',
                        title=u'Customer', conceptType=type, typeInterface=ICustomer)
        tOrder = self.addAndConfigureObject(concepts, Concept, 'order',
                        title=u'Order', conceptType=type, typeInterface=IOrder)
        # predicates:
        category_product = self.addObject(concepts, Concept, 'category.product',
                        title=u'category <- product', conceptType=predicate)
        category_accessory = self.addObject(concepts, Concept, 'category.accessory',
                        title=u'category <- accessory subcategory', conceptType=predicate)
        #category_selected = self.addObject(concepts, Concept, 'category.selected',
        #                title=u'category <- selected product', conceptType=predicate)
        product_accessory = self.addObject(concepts, Concept, 'product.accessory',
                        title=u'product <- accessory', conceptType=predicate)
        shop_product = self.addObject(concepts, Concept, 'shop.product',
                        title=u'shop <- product', conceptType=predicate)
        shop_customer = self.addObject(concepts, Concept, 'shop.customer',
                        title=u'shop <- customer', conceptType=predicate)
        #shop_order = self.addObject(concepts, Concept, 'shop.order',
        #                title=u'shop <- order', conceptType=predicate)
        manufacturer_product = self.addObject(concepts, Concept, 'manufacturer.product',
                        title=u'manufacturer <- product', conceptType=predicate)
        customer_order = self.addObject(concepts, Concept, 'customer.order',
                        title=u'customer <- order', conceptType=predicate)
        # records:
        records = self.context.getRecordManager()
        if 'orderitems' not in records:
            records['orderitems'] = TrackingStorage(trackFactory=OrderItem)
