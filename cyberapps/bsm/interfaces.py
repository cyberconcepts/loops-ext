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
Interfaces for BSM (Berlin School Managment).

$Id$
"""

from zope.interface import Interface, Attribute
from zope import schema

from loops.util import _


class ISchoolInfo(Interface):
    """ Information about schools taking part in the Berlin School Management
        (BSM) project.

        The name of the school is in the ``title`` attribute.
    """

    address = schema.TextLine(
                    title=_(u'Address'),
                    description=_(u'Postal address of the school'),
                    required=False,)
    headMaster = schema.TextLine(
                    title=_(u'Headmaster'),
                    description=_(u'Name of the head master of the school'),
                    required=False,)
    telephone = schema.TextLine(
                    title=_(u'Telephone'),
                    description=_(u'Telephone number of the headmaster'),
                    required=False,)
    telefax = schema.TextLine(
                    title=_(u'Telefax'),
                    description=_(u'Telefax number of the headmaster'),
                    required=False,)
    email = schema.TextLine(
                    title=_(u'Email'),
                    description=_(u'Email address of the headmaster'),
                    required=False,)
    website = schema.TextLine(
                    title=_(u'Website'),
                    description=_(u'URL of the website of the school'),
                    required=False,)

