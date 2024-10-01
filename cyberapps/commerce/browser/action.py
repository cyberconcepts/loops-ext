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
Action definitions for loops-based eCommerce applications.

$Id$
"""

from cyberapps.commerce.util import _
from cybertools.browser.action import actions
from loops.browser.action import DialogAction, TargetAction


actions.register('create_product', 'portlet', TargetAction,
        title=_(u'Create Product...'),
        description=_(u'Create a new product.'),
        viewName='create_product_page.html',
)

actions.register('edit_product', 'portlet', TargetAction,
        title=_(u'Edit Product...'),
        description=_(u'Modify product data.'),
        viewName='edit_product_page.html',
)

actions.register('create_category', 'portlet', TargetAction,
        title=_(u'Create Catgory...'),
        description=_(u'Create a new category.'),
        viewName='create_category_page.html',
)

actions.register('edit_category', 'portlet', TargetAction,
        title=_(u'Edit Category...'),
        description=_(u'Modify category data.'),
        viewName='edit_category_page.html',
)

actions.register('edit_customer', 'portlet', TargetAction,
        title=_(u'Edit Customer...'),
        description=_(u'Modify customer data.'),
        viewName='edit_concept_page.html',
)
