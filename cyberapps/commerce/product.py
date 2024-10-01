# cyberapps.commerce.product

""" Product adapter.
"""

from zope.app.intid.interfaces import IIntIds
from zope import component
from zope.interface import implementer

from cyberapps.commerce.interfaces import IProduct, ICategory
from cybertools.commerce.interfaces import IManufacturer, ISupplier
from cybertools.commerce.product import Product as BaseProduct, Category as BaseCategory
from cybertools.commerce.product import Manufacturer, Supplier
from cybertools.util.cache import cache
from loops.common import adapted, AdapterBase, baseObject, ParentRelation
from loops.common import ParentRelationSetProperty, ChildRelationSetProperty
from loops.interfaces import IConceptSchema
from loops.type import TypeInterfaceSourceList
from loops import util


TypeInterfaceSourceList.typeInterfaces += (
            IProduct, ICategory, IManufacturer, ISupplier)


@implementer(IProduct)
class Product(AdapterBase, BaseProduct):

    _adapterAttributes = ('context', '__parent__',
                          'shops', 'manufacturer', 'suppliers', 'categories',
                          'recommendedAccessories')
    _contextAttributes = list(IProduct)
    _noexportAttributes = ('shops', 'categories', 'manufacturer', 'suppliers',
                           'recommendedAccessories')

    shops = ParentRelationSetProperty('shop.product')
    categories = ParentRelationSetProperty('category.product')
    manufacturer = ParentRelation('manufacturer.product')
    suppliers = ParentRelationSetProperty('supplier.product')
    recommendedAccessories = ChildRelationSetProperty('product.accessory')

    @property
    def identifier(self):
        return self.productId


@implementer(ICategory)
class Category(AdapterBase, BaseCategory):

    _adapterAttributes = ('context', '__parent__',
                          'shops', 'subcategories', 'products',
                          'accessorySubcategories', 'selectedProducts')
    _contextAttributes = list(ICategory)
    _noexportAttributes = ('shops', 'products', 'parentCategories',
                           'subcategories', 'accessorySubcategories',
                           'selectedProducts')

    shops = ParentRelationSetProperty('shop.category')
    products = ChildRelationSetProperty('category.product')
    parentCategories = ParentRelationSetProperty('standard', ICategory)
    subcategories = ChildRelationSetProperty('standard')
    accessorySubcategories = ChildRelationSetProperty('category.accessory')
    selectedProducts = ChildRelationSetProperty('category.selected')

    def getLongTitle(self):
        parent = u''
        defaultPredicate = self.getLoopsRoot().getConceptManager().getDefaultPredicate()
        pr = self.context.getParentRelations([defaultPredicate])
        for r in pr:
            if r.relevance >= 0.8:
                parent = r.first.title
        if parent:
            parent = u' - ' + parent
        return self.title + parent

    def getIsActiveCacheId(self, shop=None, *args, **kw):
        shopId = shop is None and 'None' or shop.uid
        filter = kw.get('filter') or ''
        return 'commerce.category.isActive.%s.%s.%s' % (self.uid, shopId, filter)

    @cache(getIsActiveCacheId, lifetime=93600)
    def isActive(self, shop=None, filter=None):
        depth = 0
        for cat in self.subcategories:
            if ICategory.providedBy(cat):
                depth = max(depth, int(cat.isActive(shop, filter=filter)))
        if depth:
            return depth + 1
        for prod in self.products:
            if prod.isActive(shop, filter=filter):
                return True
        return False

    def getAccessoryParents(self):
        pred = self.getLoopsRoot().getConceptManager()['category.accessory']
        for c in self.context.getParents([pred]):
            yield adapted(c)

    def getAllProductsCacheId(self, shop=None, *args, **kw):
        shopId = shop is None and 'None' or shop.uid
        filter = kw.get('filter') or ''
        return 'commerce.category.allProducts.%s.%s.%s' % (self.uid, shopId, filter)

    @cache(getAllProductsCacheId, lifetime=93600)
    def getAllProductsUids(self, shop=None, filter=None):
        intids = component.getUtility(IIntIds)
        result = [util.getUidForObject(baseObject(p), intids)
                        for p in self.products
                        if p.isActive(shop, filter)]
        for c in self.subcategories:
            result.extend(c.getAllProductsUids())
        return result


class Manufacturer(AdapterBase, Manufacturer):

    _contextAttributes = list(IManufacturer)
    _noexportAttributes = ('products',)

    products = ChildRelationSetProperty('manufacturer.product')

    def getIsActiveCacheId(self, shop, *args, **kw):
        shopId = shop is None and 'None' or shop.uid
        filter = kw.get('filter') or ''
        return 'commerce.manufacturer.isActive.%s.%s.%s' % (self.uid, shopId, filter)

    @cache(getIsActiveCacheId, lifetime=72000)
    def isActive(self, shop=None, filter=None):
        for prod in self.products:
            if prod.isActive(shop, filter=filter):
                return True


class Supplier(AdapterBase, Supplier):

    _contextAttributes = list(ISupplier)
    _noexportAttributes = ('products',)

    products = ChildRelationSetProperty('supplier.product')

