#
#  Copyright (c) 2009 Helmut Merz helmutm@cy55.de
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Specific interfaces.

$Id$
"""

from cyberapps.commerce.util import _
from cybertools.commerce.interfaces import IShop, IProduct, ICategory, IManufacturer
from cybertools.commerce.interfaces import ICustomer, IAddress
from cybertools.commerce.interfaces import IOrder, IOrderItem
from loops.interfaces import ILoopsAdapter
from loops.schema.base import Relation, RelationSet


class IShop(ILoopsAdapter, IShop):

    pass


class ICategory(ILoopsAdapter, ICategory):

    accessorySubcategories = RelationSet(
            title=_(u'Accessory Subcategories'),
            description=_(u'A collection of categories that contain products '
                          u'that may be used as accessories for this category.'),
            target_types=('category',),
            required=False)
    selectedProducts = RelationSet(
            title=_(u'Selected Products'),
            description=_(u'Selected products for this category.'),
            target_types=('product',),
            required=False)


class IProduct(ILoopsAdapter, IProduct):

    shops = RelationSet(
            title=_(u'Shops'),
            description=_(u'The shops providing this product..'),
            target_types=('shop',),
            required=False)
    categories = RelationSet(
            title=_(u'Categories'),
            description=_(u'The product categories this product belongs to.'),
            target_types=('category',),
            required=False)
    manufacturer = Relation(
            title=_(u'Manufacturer'),
            description=_(u'The manufacturer providing this product.'),
            target_types=('manufacturer',),
            required=False)
    recommendedAccessories = RelationSet(
            title=_(u'Recommended Accessories'),
            description=_(u'Accessories for this product.'),
            target_types=('product',),
            required=False)


class ICustomer(ILoopsAdapter, ICustomer):

    pass


class IAddress(ILoopsAdapter, IAddress):

    pass


class IOrder(ILoopsAdapter, IOrder):

    pass

