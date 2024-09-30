#
#  Copyright (c) 2016 Helmut Merz helmutm@cy55.de
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
View classes for the CCO_R2 skin.
"""

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy

from loops.browser.concept import ConceptView as BaseConceptView
from loops.browser.lobo.standard import BasePart, Layout

template = ViewPageTemplateFile('view_macros.pt')


class LoboLayout(BasePart, Layout):

    template = template
    macroName = 'lobo-main'

    @Lazy
    def subparts(self):
        return [dict(item=self, macro=self.template.macros['lobo-part2'])]

    def getImageData(self, img):
        url = self.nodeView.getUrlForTarget(img)
        src = ('%s/mediaasset.html?v=%s' % (url, 'medium'))
        srcFull = ('%s/mediaasset.html' % (url))
        return dict(src=src, srcFull=srcFull)
