#
#  Copyright (c) 2017 Helmut Merz helmutm@cy55.de
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
Interfaces for the cco.common package.
"""

from zope.app.container.constraints import contains, containers
from zope.i18nmessageid import MessageFactory
from zope.interface import Attribute, Interface
from zope import schema

from cybertools.organize.interfaces import IAddress as IBaseAddress,\
     IPerson as IBaseContactPerson

from loops.schema.base import Relation, RelationSet
from loops.interfaces import ILoopsAdapter, IResourceAdapter

_ = MessageFactory('cco.common')


class IAttachmentType(ILoopsAdapter):
    """ A manager/container of task texts for expenditure reports.
        Usually implemented as an ITrackingStorage adapter.
    """

    sortNumber = schema.TextLine(
        title=_(u'label_sortNumber'),
        description=_(u'desc_sortNumber'),
        required=False)

    attachmentType = Relation(
        title=_(u'label_attachmentType'),
        description=_(u'label_attachmentType'),
        target_types=('attachmenttype',),
        required=False)


class ISharepointLink(IResourceAdapter):
    """ A resource containing some sort of plain text that may be rendered and
        edited without necessarily involving a special external application
        (like e.g. OpenOffice); typical content types are text/html, text/xml,
        text/restructured, etc.
    """

    attachmentType = Relation(
        title=_(u'label_attachmentType'),
        description=_(u'label_attachmentType'),
        target_types=('attachmenttype',),
        required=False)

    valueDate = schema.Datetime(
        title=_(u'Date'),
        description=_(u'Date'),
        required=False)
    # valueDate = Attribute(u'disabled for the moment')

    data = schema.Bytes(
        title=_(u'Data'),
        description=_(u'Resource raw data'),
        default='',
        missing_value='',
        required=False)

    contentType = schema.Choice(
        title=_(u'Content Type'),
        description=_(u'Content type (format) of the data field'),
        values=('text/restructured', 'text/structured', 'text/html',
                'text/plain', 'text/xml', 'text/css'),
        default='text/restructured',
        readonly=True,
        required=True)

    externalUrl = schema.TextLine(
        title=_(u'Url'),
        description=_(u'label_externalUrl'),
        required=False,
        readonly=True)

    downloadUrl = schema.TextLine(
        title=_(u'label_downloadUrl'),
        description=_(u'label_downloadUrl'),
        required=False,
        readonly=True)

    barcode = schema.TextLine(
        title=_(u'label_barcode'),
        description=_(u'An barcode link associated with the document'),
        default=u'',
        required=False)

    comments = schema.Text(
        title=_('label_comments'),
        description=_('desc_comments'),
        required=False)


class IFederalState(ILoopsAdapter):

    identifier = Attribute(u'Identifier')


class IDistrict(ILoopsAdapter):
    """ A district
    """


class ICommunity(ILoopsAdapter):
    """ A community, i.e. a city, town, or village, usually with its own
        administration (Mayor, Treasurer, ...).
    """


class IRegionalCouncil(ILoopsAdapter):
    """ A regional council 
    """


class IBranchOffice(ILoopsAdapter):
    """ A branch office
    """


class IAddress(ILoopsAdapter, IBaseAddress):
    """ A address
    """


class IContactPerson(ILoopsAdapter, IBaseContactPerson):
    """ A contact person
    """
