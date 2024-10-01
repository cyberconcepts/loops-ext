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
View classes for loops-based eCommerce applications.

$Id$
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope import component

from cybertools.browser.action import actions
from cybertools.composer.schema import Schema
from cybertools.composer.schema import Field
from loops.browser.action import DialogAction, TargetAction
from loops.browser.concept import ConceptView
from loops.browser.form import EditConceptPage, CreateConceptPage
from loops.browser.form import EditConcept, CreateConcept
from loops.browser.node import NodeView
from loops.common import adapted
from loops import util


product_macros = ViewPageTemplateFile('product.pt')


# products

class ProductView(ConceptView):

    pass


class EditProductPage(EditConceptPage):

    showAssignments = False

    def setupController(self):
        super(EditProductPage, self).setupController()
        self.registerDojoFormAllGrid()


class CreateProductPage(CreateConceptPage):

    showAssignments = False
    typeToken = '.loops/concepts/product'
    fixedType = True
    form_action = 'create_product'

    def setupController(self):
        super(CreateProductPage, self).setupController()
        self.registerDojoFormAllGrid()


class CreateProduct(CreateConcept):

    def getNameFromData(self):
        id = self.request.form.get('productId')
        if id:
            return 'p' + id


# categories

class CategoryView(ConceptView):

    @Lazy
    def macro(self):
        return product_macros.macros['category']

    @Lazy
    def subcategories(self):
        for c in self.adapted.subcategories:
            view = ConceptView(c.context, self.request)
            yield view

    @Lazy
    def products(self):
        for c in self.adapted.products:
            view = ProductView(c.context, self.request)
            yield view


class EditCategoryPage(EditConceptPage):

    #showAssignments = False

    def setupController(self):
        super(EditCategoryPage, self).setupController()
        self.registerDojoFormAllGrid()


class CreateCategoryPage(CreateConceptPage):

    #showAssignments = False
    typeToken = '.loops/concepts/category'
    fixedType = True
    form_action = 'create_category'

    def setupController(self):
        super(CreateCategoryPage, self).setupController()
        self.registerDojoFormAllGrid()


class CreateCategory(CreateConcept):

    def getNameFromData(self):
        return super(CreateCategory, self).getNameFromData()

        id = self.request.form.get('productId')
        if id:
            return 'p' + id

