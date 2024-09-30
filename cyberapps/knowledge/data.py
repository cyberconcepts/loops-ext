# cyberapps.knowlege.data

""" Classes for Knowledge and Skills Management.
"""

from zope.container.interfaces import INameChooser
from zope.component import adapts
from zope.interface import implementer
from zope.traversing.api import getName

from cyberapps.knowledge.interfaces import IJobPosition, IQualification
from cyberapps.knowledge.interfaces import IJPDescription, IIPSkillsRequired
from cyberapps.knowledge.interfaces import IQualificationsRequired
from cyberapps.knowledge.interfaces import IQualificationsRecorded
from cyberapps.knowledge.interfaces import ISkillsRecorded
from cyberapps.knowledge.interfaces import IIPSkillsQuestionnaire
from cybertools.organize.interfaces import IPerson
from loops.common import AdapterBase, adapted, baseObject
from loops.concept import Concept
from loops.interfaces import IConcept
from loops.knowledge.survey.base import Questionnaire
from loops.organize.party import getPersonForUser
from loops.setup import addObject
from loops.table import DataTable
from loops.type import TypeInterfaceSourceList
from loops import util


TypeInterfaceSourceList.typeInterfaces += (
        IJobPosition, IJPDescription, IIPSkillsRequired, 
        IQualificationsRequired, IQualification,
        IQualificationsRecorded, ISkillsRecorded,
        IIPSkillsQuestionnaire)


@implementer(IJobPosition)
class JobPosition(AdapterBase):

    def getPersons(self):
        result = [adapted(c) for c in self.context.getChildren()]
        return [p for p in result if IPerson.providedBy(p)]

    def getJPDescription(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IJPDescription.providedBy(obj):
                return obj

    def createJPDescription(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'jpdesc.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['jpdescription']
        obj = addObject(concepts, Concept, name, type=type,
                        title='JP Description: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)


    def getIPSkillsRequired(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IIPSkillsRequired.providedBy(obj):
                return obj

    def createIPSkillsRequired(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'ipsreq.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['ipskillsrequired']
        obj = addObject(concepts, Concept, name, type=type,
                        title='IP Skills Req: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)

    def getQualificationsRequired(self):
        for c in self.context.getChildren():
            obj = adapted(c)
            if IQualificationsRequired.providedBy(obj):
                return obj

    def createQualificationsRequired(self):
        concepts = self.getLoopsRoot().getConceptManager()
        name = 'qureq.' + self.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['qualificationsrequired']
        obj = addObject(concepts, Concept, name, type=type,
                        title='Qualifications Req: ' + self.title)
        self.context.assignChild(obj)
        return adapted(obj)


@implementer(IJPDescription)
class JPDescription(AdapterBase):

    _contextAttributes = AdapterBase._contextAttributes + list(IJPDescription)


@implementer(IIPSkillsRequired)
class IPSkillsRequired(AdapterBase):

    _contextAttributes = AdapterBase._contextAttributes + list(IIPSkillsRequired)


@implementer(IQualificationsRequired)
class QualificationsRequired(AdapterBase):

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(IQualificationsRequired))


@implementer(IQualification)
class Qualification(DataTable):

    _contextAttributes = AdapterBase._contextAttributes + list(IQualification)


@implementer(IQualificationsRecorded)
class QualificationsRecorded(AdapterBase):

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(IQualificationsRecorded))


@implementer(ISkillsRecorded)
class SkillsRecorded(AdapterBase):

    _contextAttributes = (AdapterBase._contextAttributes + 
                            list(ISkillsRecorded))


@implementer(IIPSkillsQuestionnaire)
class IPSkillsQuestionnaire(Questionnaire):

    def getQuestionGroups(self, personId=None):
        if personId is None:
            person = getPersonForUser(self.context)
        else:
            person = util.getObjectForUid(personId)
        result = []
        required = self.getRequiredIPSkills(person)
        groups = super(IPSkillsQuestionnaire, self).getQuestionGroups()
        if not required:
            return groups
        for group in groups:
            skills = self.getIPSkillsForGroup(group)
            if skills:
                for skill in skills:
                    if skill in required:
                        result.append(group)
                        break
            else:
                result.append(group)
        return result

    def getIPSkillsForGroup(self, group):
        result = []
        for p in baseObject(group).getParents():
            if getName(p.conceptType) == 'ipskill':
                result.append(adapted(p))
        return result

    def getRequiredIPSkills(self, person):
        result = []
        for p in person.getParents():
            job = adapted(p)
            if IJobPosition.providedBy(job):
                ipskills = job.getIPSkillsRequired()
                if ipskills is not None:
                    requirements = ipskills.requirements
                    for item in requirements.values():
                        if item.get('selected'):
                            result.append(util.getObjectForUid(item['uid']))
        return result
