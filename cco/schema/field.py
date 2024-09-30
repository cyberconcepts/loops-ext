#
#  Copyright (c) 2020 Helmut Merz helmutm@cy55.de
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
Field and field instance classes for URLs and other stuff.
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.schema import Field

from cybertools.composer.schema.field import FieldInstance
from cybertools.composer.schema.interfaces import FieldType


schema_macros = ViewPageTemplateFile('view_macros.pt')


class UrlField(Field):

    __typeInfo__ = ('url',
                    FieldType('url', 'url',
                              u'A field representing a URL.',
                              instanceName='url',
                              displayRenderer='display_url',
                              inputRenderer='input_textline'))



class UrlFieldInstance(FieldInstance):

    def display(self, value):
        return value

    def getRenderer(self, name):
        return schema_macros.macros[name]

