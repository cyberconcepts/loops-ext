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
Definition of classes for viewing reporting data in cyberapps.knowledge.
"""

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

from loops.common import adapted, baseObject
from loops.knowledge.survey.interfaces import IQuestionGroup
from loops.knowledge.survey.response import Responses
from loops import util
from cyberapps.knowledge.browser.qualification import \
        JobPositionsOverview, PositionView, JPDescForm
from cyberapps.knowledge.browser.qualification import template as baseTemplate
from cyberapps.knowledge.interfaces import IQualificationsRecorded

_ = MessageFactory('cyberapps.knowledge')


template = ViewPageTemplateFile('report_macros.pt')


class ReportBaseView(object):

    template = template
    templateName = 'knowledge.report'
    baseTemplate = baseTemplate


class JobsListing(ReportBaseView, JobPositionsOverview):

    macroName = 'jobs'

    def update(self):
        instUid = self.request.form.get('select_institution')
        if instUid:
            return self.setInstitution(instUid)

    def getItemUrl(self, item):
        itemViewName = self.options('item_viewname')
        baseUrl = self.nodeView.getUrlForTarget(item)
        if itemViewName:
            return '/'.join((baseUrl, itemViewName[0]))
        return baseUrl


class JobDescription(ReportBaseView, JPDescForm):

    macroName = 'jobdescription'
    parentName = None

    def getData(self):
        self.setupController()
        self.registerDojoSlider()
        result = dict(header={}, administrative=[], workdesc=[], 
                      qualifications=[], ipskills=[])
        data = dict(header={}, administrative={}, workdesc={}, 
                    qualifications={}, ipskills={})
        # load data
        jp = adapted(self.target)
        jpDesc = jp.getJPDescription()
        if jpDesc is not None:
            if jpDesc.administrativeData:
                data['administrative'] = jpDesc.administrativeData
            if jpDesc.workDescription:
                data['workdesc'] = jpDesc.workDescription
            if jpDesc.header:
                data['header'] = result['header'] = jpDesc.header
        qureq = adapted(self.target).getQualificationsRequired()
        if qureq is not None:
            data['qualifications'] = qureq.requirements
        skillsreq = adapted(self.target).getIPSkillsRequired()
        if skillsreq is not None:
            data['ipskills'] = skillsreq.requirements
        # administrative data
        adminDT = adapted(self.conceptManager['jpdesc_administrative'])
        for row in adminDT.data.values():
            key, label, desc, optional = row
            dataRow = data['administrative'].get(key) or {}
            if dataRow.get('inactive'):
                continue
            result['administrative'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or u''))
        # work description
        workdescDT = adapted(self.conceptManager['jpdesc_workdesc'])
        for row in workdescDT.data.values():
            key, label, desc, optional = row
            dataRow = data['workdesc'].get(key) or {}
            if dataRow.get('inactive'):
                continue
            result['workdesc'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or (5 * [u''])))
        # qualifications
        qualifications = self.conceptManager['qualifications']
        for obj in qualifications.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(obj)
            dataRow = data['qualifications'].get(uid) or {}
            item = dict(key=uid, label=obj.title, 
                        desc=obj.description, schema=[],
                        value=dataRow.get('value') or (3 * [u'']),
                        req=dataRow.get('req') or (3 * [u'0']))
            for row in adapted(obj).data.values():
                if len(row) < 5:
                    continue
                key = row[0]
                value = dataRow.get('qu_' + key) or (3 * [u''])
                item['schema'].append(dict(                            
                            key=key, label=row[1], 
                            level=row[2], type=row[4], 
                            value=value))
            result['qualifications'].append(item)
        # ipskills
        ipskills = self.conceptManager['ipskills']
        for parent in ipskills.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(parent)
            item = dict(uid=uid, label=parent.title, 
                        description=parent.description, skills=[])
            for child in parent.getChildren([self.defaultPredicate]):
                uid = util.getUidForObject(child)
                row = data['ipskills'].get(uid) or {}
                if row.get('selected'):
                    item['skills'].append(
                        dict(uid=uid, label=child.title,
                             description=child.description,
                             expected=row.get('expected') or 0))
            result['ipskills'].append(item)
        return result


class JobReport(ReportBaseView, PositionView):

    macroName = 'job_report'
    parentName = 'qkb'

    qualificationData = None
    questionnaires = None
    quGroups = None
    ipskillsInputData = None

    def getData(self):
        self.setupController()
        self.registerDojoCharting()
        lang = self.languageInfo.language
        result = dict(qualifications=[], ipskills=[])
        reqData = dict(qualifications={}, ipskills={})
        persons = self.adapted.getPersons()
        selectedPerson = self.request.form.get('person')
        if selectedPerson:
            p = adapted(util.getObjectForUid(selectedPerson))
            if p in persons:
                persons = [p]
        # load requirement data
        qureq = adapted(self.target).getQualificationsRequired()
        if qureq is not None:
            reqData['qualifications'] = qureq.requirements
        skillsreq = adapted(self.target).getIPSkillsRequired()
        if skillsreq is not None:
            reqData['ipskills'] = skillsreq.requirements
        # qualification data
        qualifications = self.conceptManager['qualifications']
        for obj in qualifications.getChildren([self.defaultPredicate]):
            qualification = adapted(obj)
            uid = qualification.uid
            dataRow = reqData['qualifications'].get(uid) or {}
            personData = self.getQualificationData(uid, persons)
            item = dict(key=uid, label=qualification.title, 
                        desc=qualification.description, schema=[],
                        value=dataRow.get('value') or (3 * [u'']),
                        req=dataRow.get('req') or (3 * [u'0']),
                        personData=personData)
            for row in qualification.data.values():
                if len(row) < 5:
                    continue
                key = row[0]
                value = dataRow.get('qu_' + key) or (3 * [u''])
                item['schema'].append(dict(                            
                            key=key, label=row[1], 
                            level=row[2], type=row[4], 
                            value=value))
            result['qualifications'].append(item)
        # ipskills data
        ipskills = self.conceptManager['ipskills']
        for parent in ipskills.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(parent)
            item = dict(uid=uid, label=parent.title, 
                        description=parent.description, skills=[])
            for child in parent.getChildren([self.defaultPredicate]):
                uid = util.getUidForObject(child)
                row = reqData['ipskills'].get(uid) or {}
                if row.get('selected'):
                    ipskillsInput = self.getIPSkillsInput(child, persons)
                    v = int(row.get('expected') or 0) + 1
                    vstr = '%s: %s' % (
                        translate(_('ipskills_required'), target_language=lang), v)
                    item['skills'].append(
                        dict(uid=uid, label=child.title,
                             description=child.description,
                             expected=v,
                             expStr=vstr,
                             ipskillsInput=ipskillsInput))
            result['ipskills'].append(item)
        return result

    def getQualificationData(self, quUid, persons):
        result = []
        personUids = [p.uid for p in persons]
        if self.qualificationData is None:
            self.qualificationData = {}
            for p in persons:
                for c in baseObject(p).getChildren():
                    obj = adapted(c)
                    if IQualificationsRecorded.providedBy(obj):
                        self.qualificationData[p.uid] = obj.data
                        break
                else:
                    self.qualificationData[p.uid] = {}
        for p in persons:
            data = self.qualificationData[p.uid].get(quUid) or {}
            if data:
                item = dict(name=p.title)
                item.update(data)
                result.append(item)
        return result

    def getIPSkillsInput(self, competence, persons):
        result = []
        lang = self.languageInfo.language
        personUids = [p.uid for p in persons]
        questionGroup = refQuestionGroup = None
        for c in baseObject(competence).getChildren():
            qug = adapted(c)
            if IQuestionGroup.providedBy(qug):
                questionnaire = self.getQuestionnaire(qug, 'standard')
                if (questionnaire is not None and 
                        qug in self.quGroups.get('standard')):
                    questionGroup = qug
                else:
                    refQuestionnaire = self.getQuestionnaire(qug, 'person')
                    if (refQuestionnaire is not None and 
                            qug in self.quGroups.get('person')):
                        refQuestionGroup = qug
                    #break
        if questionGroup is None and refQuestionGroup is None:
            return result
        if self.ipskillsInputData is None:
            self.ipskillsInputData = {}
            for uid in personUids:
                respManager = Responses(baseObject(questionnaire))
                self.ipskillsInputData[uid] = respManager.load(uid)
                if refQuestionGroup is not None:
                    refRespManager = Responses(baseObject(refQuestionnaire))
                    self.ipskillsInputData[uid].update(
                                refRespManager.loadRange(uid + '.*'))
        for idx, uid in enumerate(personUids):
            person = persons[idx]
            data = self.ipskillsInputData.get(uid)
            if data is not None:
                value = data.get(questionGroup.uid)
                refValues = refQuestionGroup and data.get(refQuestionGroup.uid)
                if value is None and refValues is None:
                    continue
                item = dict(name=person.title, value=None, avg=None, vstr=None,
                            refValues=dict(values=[], avg=None, vstr=None))
                if value is not None:
                    v = int(round(value * 4 + 1))
                    item['value'] = v
                    item['vstr'] = '%s: %s' % (
                        translate(_('label_skillValues'), target_language=lang), v)
                if refValues:
                    refValues = sorted([int(round(v * 4 + 1)) for v in refValues])
                    avg = int(round(sum(refValues) / len(refValues)))
                    vstr = '%s: %s' % (
                        translate(_('label_refValues'), target_language=lang), 
                        ', '.join(str(v) for v in refValues))
                    item['refValues']=dict(values=refValues, avg=avg, vstr=vstr)
                result.append(item)
        return result

    def getQuestionnaire(self, quGroup, quType):
        if self.questionnaires is None:
            self.questionnaires = {}
            self.quGroups = {}
        if quType in self.questionnaires:
            return self.questionnaires[quType]
        for qu in quGroup.getQuestionnaires():
            if qu.questionnaireType == quType:
                self.questionnaires[quType] = qu
                self.quGroups[quType] = qu.getAllQuestionGroups()
                break
        return self.questionnaires.get(quType)
