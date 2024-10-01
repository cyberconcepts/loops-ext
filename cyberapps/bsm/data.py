# cyberapps.bsm.data

""" Classes for BSM School Informations.
"""

from zope.component import adapts
from zope.interface import implementer

from cyberapps.bsm.interfaces import ISchoolInfo
from loops.common import AdapterBase
from loops.interfaces import IConcept
from loops.type import TypeInterfaceSourceList


TypeInterfaceSourceList.typeInterfaces += (ISchoolInfo,)


@implementer(ISchoolInfo)
class SchoolInfoAdapter(AdapterBase):

    _contextAttributes = list(ISchoolInfo) + list(IConcept)

