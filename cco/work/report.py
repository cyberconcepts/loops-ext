# cco.work.report

""" Report class(es) for the cco.work package.
"""

from cybertools.util.jeep import Jeep
from loops.common import adapted, baseObject
from loops.expert.field import Field, DecimalField, TargetField, UrlField
from loops.expert.report import ReportInstance
from loops.organize.work.report import DurationField
from cco.work.interfaces import IProject, ITask, _


task = UrlField('title', _(u'colheader_task'),
                executionSteps=['sort', 'output'])
estimatedEffort = DurationField(
                    'estimatedEffort', _(u'colheader_estimatedEffort'),
                    factor = 3600,
                    executionSteps=['output', 'totals'])
chargedEffort = DurationField('chargedEffort', _(u'colheader_chargedEffort'),
                    factor = 3600,
                    executionSteps=['output', 'totals'])
actualEffort = DurationField('actualEffort', _(u'colheader_actualEffort'),
                    executionSteps=['output', 'totals'])


class TasksOverview(ReportInstance):

    type = 'cco.work.tasks_overview'
    label = u'Tasks Overview'

    fields = Jeep((task, estimatedEffort, chargedEffort, actualEffort))
    #userSettings = (dayFrom, dayTo, activity)
    defaultOutputFields = fields
    defaultSortCriteria = (task,)

    def selectObjects(self, parts):
        result = []
        for c in baseObject(self.view.adapted).getChildren():
            obj = adapted(c)
            if IProject.providedBy(obj) or ITask.providedBy(obj):
                result.append(obj)
        return result
