# cyberapps.ccmkg.data

""" Classes for Cyberconcepts Marketing.
"""

from zope.component import adapts
from zope.interface import implementer

from cyberapps.ccmkg.interfaces import IProjectReference
from loops.common import AdapterBase
from loops.interfaces import IConcept
from loops.type import TypeInterfaceSourceList


TypeInterfaceSourceList.typeInterfaces += (IProjectReference,)


@implementer(IProjectReference)
class ProjectReferenceAdapter(AdapterBase):

    _contextAttributes = list(IProjectReference) + list(IConcept)

