# cco.work.task

""" Implementation of cco.work concepts.
"""

from zope.cachedescriptors.property import Lazy
from zope.interface import implementer

from cybertools.organize.interfaces import IWorkItems
#from cco.storage.loops.common import AdapterBase
from loops.common import AdapterBase
from loops.common import adapted, baseObject
#from loops.organize.task import Task
from loops.type import TypeInterfaceSourceList
from loops import util
from cco.work.interfaces import IProject, ITask


TypeInterfaceSourceList.typeInterfaces += (IProject, ITask)


class TaskBase(AdapterBase):

    _contextAttributes = list(ITask)

    #start = end = None

    defaultStates = ['done', 'done_x', 'finished', 'finished_x']

    @property
    def actualEffort(self):
        result = 0.0
        for t in self.getAllTasks():
            for wi in t.getWorkItems():
                result += wi.effort
        return result

    def getSubTasks(self):
        if self.__is_dummy__:
            return []
        result = []
        for c in baseObject(self).getChildren():
            obj = adapted(c)
            if IProject.providedBy(obj) or ITask.providedBy(obj):
                result.append(obj)
        return result

    def getAllTasks(self):
        if self.__is_dummy__:
            return []
        result = set([self])
        for t1 in self.getSubTasks():
            if t1 not in result:
                for t2 in t1.getAllTasks():
                    if t2 not in result:
                        result.add(t2)
        return result

    @Lazy
    def workItems(self):
        rm = self.getLoopsRoot().getRecordManager()
        return IWorkItems(rm['work'])

    def addWorkItem(self, party, action='plan', **kw):
        wi = self.workItems.add(util.getUidForObject(baseObject(self)), party)
        wi.doAction(action, party, **kw)

    def getWorkItems(self, crit={}):
        kw = dict(task=util.getUidForObject(baseObject(self)), 
                  state=crit.get('states') or self.defaultStates)
        return self.workItems.query(**kw)


@implementer(IProject)
class Project(TaskBase):
    """ Adapter for concepts of a project type
        with additional fields for planning/controlling.
    """

    _adapterAttributes = AdapterBase._adapterAttributes + (
            'estimatedEffort', 'chargedEffort', 'actualEffort',)
    _contextAttributes = list(IProject)

    @property
    def estimatedEffort(self):
        return sum(self.tofloat(t.estimatedEffort or 0.0) 
                    for t in self.getSubTasks())

    @property
    def chargedEffort(self):
        return sum(self.tofloat(t.chargedEffort or 0.0) 
                    for t in self.getSubTasks())

    @staticmethod
    def tofloat(v):
        if isinstance(v, str):
            v = v.replace(',', '.')
        try:
            return float(v)
        except ValueError:
            return 0.0


@implementer(ITask)
class Task(TaskBase):
    """ Adapter for concepts of a task type
        with additional fields for planning/controlling.
    """

    #estimatedEffort = chargedEffort = 0.0

    _adapterAttributes = AdapterBase._adapterAttributes + ('actualEffort',)
    _contextAttributes = list(ITask)

