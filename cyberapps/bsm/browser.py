#
#  Copyright (c) 2007 Helmut Merz helmutm@cy55.de
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
View classes for the BSM (Berlin School Management) project.

$Id$
"""

from zope import interface, component
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy

from cybertools.composer.schema import Schema
from cybertools.composer.schema import Field
from cybertools.reporter.browser.report import DetailView, ListingView
from cybertools.reporter.resultset import ResultSet, Cell
from loops.browser.concept import ConceptView
from loops.browser.node import NodeView
from loops.common import adapted
from loops.browser.common import conceptMacrosTemplate
from loops import util


bsmTemplate = ViewPageTemplateFile('macros.pt')


class TitleCell(Cell):

    @property
    def url(self):
        view = self.row.resultSet.view
        if view is None:
            return u''
        return ('%s/.target%s' %
                (view.url, util.getUidForObject(self.row.context.context)))


class UrlCell(Cell):

    limit = None

    @property
    def url(self):
        value = self.value
        if not value:
            return ''
        if self.field.name == 'email':
            return 'mailto:' + value
        if value.startswith('http'):
            return value
        return 'http://' + value

    @property
    def text(self):
        text = super(UrlCell, self).text
        if self.limit and len(text) > self.limit:
            text = text[:self.limit-1] + '...'
        return text


class UrlCellWithLimit(UrlCell):

    limit = 20


class SchoolDetails(DetailView):

    conceptMacros = conceptMacrosTemplate

    @property
    def macro(self):
        return bsmTemplate.macros['detail']

    @Lazy
    def nodeView(self):
        return NodeView(self.context, self.request)

    def resources(self):
        for obj in self.context.getResources():
            yield ConceptView(obj, self.request)

    @Lazy
    def resultSet(self):
        result = ResultSet([adapted(self.context)])
        result.schema = Schema(
            Field(u'title', u'Name'),
            Field(u'address', u'Anschrift'),
            Field(u'headMaster', u'Rektor'),
            Field(u'telephone', u'Telefon'),
            Field(u'telefax', u'Telefax'),
            Field(u'email', u'E-Mail', renderFactory=UrlCell),
            Field(u'website', u'Web', renderFactory=UrlCell),
        )
        result.view = self.nodeView
        return result


class SchoolListing(ListingView):

    @property
    def children(self):
        for obj in self.nodeView.virtualTargetObject.getChildren():
            yield adapted(obj)

    @Lazy
    def nodeView(self):
        return NodeView(self.context, self.request)

    @Lazy
    def resultSet(self):
        result = ResultSet(self.children)
        result.schema = Schema(
            Field(u'title', u'Name', renderFactory=TitleCell),
            Field(u'address', u'Anschrift'),
            Field(u'headMaster', u'Rektor'),
            Field(u'telephone', u'Telefon'),
            Field(u'telefax', u'Telefax'),
            Field(u'email', u'E-Mail', renderFactory=UrlCellWithLimit),
            Field(u'website', u'Web', renderFactory=UrlCellWithLimit),
        )
        result.view = self.nodeView
        return result
