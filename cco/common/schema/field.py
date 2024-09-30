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
Custom field instance classes.
"""

from zope import schema

from cybertools.composer.schema.interfaces import FieldType
from cybertools.composer.schema.field import \
    DecimalFieldInstance as BaseDecimalFieldInstance
from cybertools.util.format import formatNumber

from cco.common.util import parseNumber


class DecimalField(schema.Float):

    __typeInfo__ = ('decimal',
                    FieldType('decimal',
                              'decimal',
                              u'ais specific decimal field ',
                              inputRenderer='input_textline',
                              instanceName='decimal'))


class DecimalFieldInstance(BaseDecimalFieldInstance):

    def marshall(self, value):
        return self.display(value, pattern=u'#,##0.00;-#,##0.00')

    def display(self, value,  pattern=u'#,##0.00;-#,##0.00'):
        if not value:
            return ''
        try:
            value = float(value)
        except ValueError:
            value = float(parseNumber(value))
        return formatNumber(value, pattern=pattern)

    def unmarshall(self, value):
        if not value:
            return 0.0
        return parseNumber(value)
