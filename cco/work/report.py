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
Report class(es) for the cco.work package.
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
