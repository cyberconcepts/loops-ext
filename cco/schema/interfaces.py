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
Interfaces for controlling and configuring schemas.
"""

from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope import schema

from cybertools.composer.schema.grid.interfaces import Records
from loops.util import KeywordVocabulary


_ = MessageFactory('cco.schema')


class ISchemaController(Interface):

    scInterface = schema.Choice(
        title=_(u'Schema Controller Interface'),
        description=_(u'The interface this schema controller is used for.'),
        default=None,
        source='loops.TypeInterfaceSource',
        required=False)

    schemaData = Records(
        title=_(u'Schema Data'),
        description=_(u'Schema Data'),
        default=[],
        required=False)

    scInterface.suppress = True

    schemaData.column_types = [
            schema.Text(__name__='fieldName', title=_(u'Field Name')),
            schema.Text(__name__='help_reference', title=_(u'Help Reference')),
            schema.Choice(__name__='required', title=_(u'required'),
                source=KeywordVocabulary((
                    ('required', _(u'required')),
                    ('optional', _(u'optional')),))),
            schema.Choice(__name__='editable', title=_(u'editable'),
                source=KeywordVocabulary((
                    ('editable', _(u'editable')),
                    ('hidden', _(u'hidden')),))),
            schema.Choice(__name__='display', title=_(u'display'),
                source=KeywordVocabulary((
                    ('visible', _(u'visible')),
                    ('hidden', _(u'hidden')),))),
    ]
