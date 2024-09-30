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
View classes for cyberconcepts marketing.

$Id$
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy

from cybertools.composer.schema import Schema
from cybertools.composer.schema import Field
from cybertools.reporter.browser.report import DetailView, ListingView
from cybertools.reporter.resultset import ResultSet, Cell
#from loops.browser.node import NodeView
from loops.browser.action import DialogAction
from loops.browser.concept import ConceptView
from loops.common import adapted
from loops import util


class ProjectDetail(ConceptView, DetailView):

    def getActions(self, category='object', page=None, target=None):
        actions = []
        if category == 'portlet':
            actions.append(DialogAction(self, title='Edit Project Reference...',
                  description='Modify project reference.',
                  viewName='edit_concept.html',
                  dialogName='editProjectReference',
                  page=page, target=target))
        return actions



listingTemplate = ViewPageTemplateFile('macros.pt')


class ProjectListing(ConceptView, ListingView):

    @property
    def macro(self):
        return listingTemplate.macros['listing']

    def getActions(self, category='object', page=None, target=None):
        actions = []
        if category == 'portlet':
            actions.append(DialogAction(self, title='Create Project Reference...',
                  description='Create a new project reference.',
                  viewName='create_concept.html',
                  dialogName='createProjectReference',
                  typeToken='.loops/concepts/projectreference',
                  fixedType=True,
                  innerForm='inner_concept_form.html',
                  page=page, target=target))
        return actions

    @property
    def children(self):
        objs = sorted((adapted(c) for c in self.context.getChildren(sort=None)),
                      key=lambda x: x.timeRange, reverse=True)
        return objs

    @Lazy
    def resultSet(self):
        result = ResultSet(self.children)
        result.schema = Schema(
            Field(u'title'),
            Field(u'timeRange', u'Zeitraum'),
            Field(u'customerInfo', u'Kunde'),
            Field(u'task', u'Taetigkeit'),
            Field(u'technology', u'Technik'),
        )
        result.view = self
        return result

