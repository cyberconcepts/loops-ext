#
#  Copyright (c) 2018 Helmut Merz helmutm@cy55.de
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
Common base classes.
"""

from zope.app.security.interfaces import PrincipalLookupError
from zope.cachedescriptors.property import Lazy
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.api import getName

from cybertools.util.date import formatTimeStamp

from loops.common import adapted, baseObject, AdapterBase as BaseAdapterBase
from loops.organize.util import getPrincipalForUserId
from loops.organize.party import getAuthenticationUtility, getPersonForUser
from loops.predicate import adaptedRelation


class AdapterBase(BaseAdapterBase):

    def getFullIdentifier(self):
        if self.__is_dummy__:
            return u''
        result = getName(self.context)
        prefix = adapted(self.context.conceptType).namePrefix
        if prefix:
            if prefix in getName(self.context):
                result = getName(self.context)[len(prefix):]
        return result

    @property
    def identifier(self):
        result = self.getFullIdentifier()
        if result.find('_') >= 0:
            result = result[:result.find('_')]
        return result

    def getLongTitle(self):
        if self.description:
            return self.description
        return self.title

    @property
    def longTitle(self):
        return self.getLongTitle()

    @property
    def longName(self):
        return self.title

    @Lazy
    def creationDate(self):
        dc = IZopeDublinCore(baseObject(self), None)
        if dc is not None:
            return dc.created

    @Lazy
    def creator(self):
        dc = IZopeDublinCore(baseObject(self), None)
        if dc is not None:
            for creator in dc.creators:
                person = getPersonForUser(self.context,
                                          self.request,
                                          getPrincipalForUserId(creator))
                return adapted(person)

    @Lazy
    def conceptManager(self):
        return self.context.getConceptManager()

    @Lazy
    def attachmentType(self):
        return self.conceptManager['sharepointlink']

    @Lazy
    def branchOfficeType(self):
        return self.conceptManager['branchoffice']

    @Lazy
    def typeConcept(self):
        return self.conceptManager['type']

    @Lazy
    def hasTypePredicate(self):
        return self.conceptManager['hasType']

    @Lazy
    def followsPredicate(self):
        return self.conceptManager['follows']

    @Lazy
    def defaultPredicate(self):
        return self.conceptManager['standard']

    def getRelationRole(self, child, predicate, parent=None):
        child = baseObject(child)
        if parent is None:
            parent = self
        cr = baseObject(parent).getChildRelations([predicate], child=child)
        if not cr:
            return None
        relation = cr[0]
        return adaptedRelation(relation).role

    def getRelationRoles(self, child, predicate, parent=None):
        child = baseObject(child)
        if parent is None:
            parent = self
        cr = baseObject(parent).getChildRelations([predicate], child=child)
        if not cr:
            return []
        return [adaptedRelation(r).role for r in cr]

    def getPrincipalForUserId(self, userId=None):
        userId = userId or self.userId
        if not userId:
            return None
        auth = getAuthenticationUtility(self.context)
        try:
            return auth.getPrincipal(userId)
        except PrincipalLookupError:
            return None

    @Lazy
    def currentDate(self):
        return formatTimeStamp(None, format='%d.%m.%Y')

    @Lazy
    def currentMonth(self):
        return formatTimeStamp(None, format='%m.%Y')

    def getAttachments(self):
        return [adapted(r) for r in self.context.getResources()
                if r.getType() == self.attachmentType]
