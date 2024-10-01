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
Common base/common view classes for loops-based eCommerce applications.

$Id$
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope import component

from loops.browser.concept import ConceptView
from loops.common import adapted
from loops import util


base_macros = ViewPageTemplateFile('base.pt')


class SimpleListing(ConceptView):

    @Lazy
    def macro(self):
        return base_macros.macros['simple_listing']
