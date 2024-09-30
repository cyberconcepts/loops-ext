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
Interfaces for organizational stuff like persons, addresses, tasks, ...

$Id$
"""

from zope.interface import Interface, Attribute
from zope import schema

from loops.interfaces import IConceptSchema, ILoopsAdapter
from loops.util import _


class IProjectReference(IConceptSchema, ILoopsAdapter):
    """ Project information to be used as customer reference for
        marketing purposes.
    """

    customerInfo = schema.TextLine(
                    title=_(u'Customer'),
                    description=_(u'Short description or - if appropriate - '
                        'name of the customer'),
                    required=False,)
    timeRange = schema.TextLine(
                    title=_(u'Time range'),
                    description=_(u'Info about the time range of the project'),
                    required=False,)
    task = schema.TextLine(
                    title=_(u'Task'),
                    description=_(u'Short description of our task in the project'),
                    required=False,)
    technology = schema.TextLine(
                    title=_(u'Technology'),
                    description=_(u'Info about the technology employed in '
                        'the project'),
                    required=False,)

