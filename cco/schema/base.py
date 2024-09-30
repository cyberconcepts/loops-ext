# cco.schema.base

""" A concept adapter to be used as a schema controller.
"""

from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

from cco.schema.interfaces import ISchemaController
from loops.common import AdapterBase
from loops.type import TypeInterfaceSourceList


_ = MessageFactory('cco.schema')

TypeInterfaceSourceList.typeInterfaces += (ISchemaController,)


@implementer(ISchemaController)
class SchemaController(AdapterBase):

    _contextAttributes = AdapterBase._contextAttributes + list(ISchemaController)

    #schemaData = []
