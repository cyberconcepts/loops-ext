#
#  Copyright (c) 2015 Helmut Merz helmutm@cy55.de
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
Definition of view classes and other browser related stuff for the
cyberapps.knowledge package.

Person data (competences, preferences, qualifications) views.
"""

from zope.app.container.interfaces import INameChooser
from zope import interface, component
from zope.app.container.interfaces import INameChooser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate
from zope.cachedescriptors.property import Lazy
from zope.traversing.api import getName

from cybertools.organize.interfaces import IPerson
from cybertools.stateful.interfaces import IStateful
from loops.browser.concept import ConceptView
from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.knowledge.survey.interfaces import IQuestionnaire
from loops.organize.party import getPersonForUser
from loops.setup import addObject
from loops import util

from cyberapps.knowledge.browser.qualification import QualificationBaseView
from cyberapps.knowledge.browser.qualification import template as baseTemplate
from cyberapps.knowledge.interfaces import IJobPosition
from cyberapps.knowledge.interfaces import IQualificationsRecorded, ISkillsRecorded
from cyberapps.knowledge.interfaces import _


template = ViewPageTemplateFile('person_macros.pt')


class JobPersonsOverview(QualificationBaseView, ConceptView):

    template = template
    baseTemplate = baseTemplate
    macroName = 'persons'

    def update(self):
        form = self.request.form
        instUid = form.get('select_institution')
        if instUid:
            return self.setInstitution(instUid)

    @Lazy
    def persons(self):
        self.setupController()
        result = {}
        if self.options('hide_master'):
            result ['master'] = []
        else:
            result['master'] = [PersonView(p, self.request)
                    for p in self.institution.getChildren([self.masterPredicate])]
        result['member'] = [PersonView(p, self.request)
                for p in self.institution.getChildren([self.memberPredicate])]
        result['other'] = [PersonView(p, self.request,)
                for p in self.institution.getChildren([self.defaultPredicate])
                if IPerson.providedBy(adapted(p))]
        return result


class PersonView(QualificationBaseView, ConceptView):

    template = template
    baseTemplate = baseTemplate

    pageTitle = None

    @Lazy
    def title(self):
        return self.getTitle()

    def getTitle(self):
        if self.pageTitle is None:
            return self.context.title
        lang = self.languageInfo.language
        pageTitle = translate(_(self.pageTitle), target_language=lang)
        return '%s: %s' % (pageTitle, self.context.title)

    @Lazy
    def breadcrumbsParent(self):
        for p in self.context.conceptType.getParents([self.queryTargetPredicate]):
            return self.nodeView.getViewForTarget(p)
        for p in self.context.getParents([self.queryTargetPredicate]):
            return self.nodeView.getViewForTarget(p)

    @Lazy
    def jobs(self):
        result = []
        for ch in self.institution.getChildren([self.defaultPredicate]):
            job = adapted(ch)
            if IJobPosition.providedBy(job):
                result.append(job)
        return result

    def jobAssignments(self):
        jobs = []
        for p in self.context.getParents([self.defaultPredicate]):
            job = adapted(p)
            if IJobPosition.providedBy(job):
                jobs.append(job)
        if jobs:
            state = 'active'
            text = 'active'
        else:
            state = 'none'
            text = 'to be done'
        action = 'edit_jobassignments.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        return dict(text=text, editUrl=editUrl, jobs=jobs)

    def qualifications(self):
        qualifications = self.getQualifications(adapted(self.target))
        if qualifications is None:
            state = 'none'
            text = 'to be done'
        else:
            stf = component.getAdapter(baseObject(qualifications), IStateful, 
                                       name='task_states')
            state = stf.state
            text = stf.getStateObject().title
        action = 'edit_qualifications.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        return dict(text=text, editUrl=editUrl)

    def skills(self):
        skills = self.getSkills(adapted(self.target))
        if not skills:
            state = 'none'
            text = 'to be done'
        else:
            stf = component.getAdapter(baseObject(skills), IStateful, 
                                       name='task_states')
            state = stf.state
            text = stf.getStateObject().title
        action = 'edit_skills.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        return dict(text=text, editUrl=editUrl)

    def ipskills(self):
        ipskills = []
        if not ipskills:
            state = 'none'
            text = 'to be done'
        questionnaire = None
        for ch in self.breadcrumbsParent.context.getChildren(
                            [self.defaultPredicate]):
            qu = adapted(ch)
            if IQuestionnaire.providedBy(qu):
                questionnaire = ch
                break
        if questionnaire is None:
            return dict(text='questionnaire missing', editUrl=None)
        personUid = util.getUidForObject(self.context)
        storage = self.loopsRoot['records']['survey_responses']
        tracks = storage.getUserTracks(qu.uid, 0, personUid)
        if tracks:
            #text = state = 'draft'
            text = state = tracks[0].data.get('state') or 'draft'
        editUrl = '%s?person=%s' % (
                        self.nodeView.getUrlForTarget(questionnaire), personUid)
        return dict(text=text, editUrl=editUrl)

    def preferences(self):
        preferences = []
        if not preferences:
            state = 'none'
            text = 'to be done'
        questionnaire = None
        idx = 0
        for ch in self.breadcrumbsParent.context.getChildren(
                            [self.defaultPredicate]):
            qu = adapted(ch)
            if IQuestionnaire.providedBy(qu):
                if idx > 0:
                    questionnaire = ch
                    break
                idx += 1
        if questionnaire is None:
            return dict(text='questionnaire missing', editUrl=None)
        personUid = util.getUidForObject(self.context)
        storage = self.loopsRoot['records']['survey_responses']
        tracks = storage.getUserTracks(qu.uid, 0, personUid)
        if tracks:
            text = state = 'draft'
        editUrl = '%s?person=%s' % (
                        self.nodeView.getUrlForTarget(questionnaire), personUid)
        return dict(text=text, editUrl=editUrl)

    def getQualifications(self, person):
        for c in baseObject(person).getChildren():
            obj = adapted(c)
            if IQualificationsRecorded.providedBy(obj):
                return obj

    def getSkills(self, person):
        for c in baseObject(person).getChildren():
            obj = adapted(c)
            if ISkillsRecorded.providedBy(obj):
                return obj


class ReferredListing(JobPersonsOverview):

    macroName = 'referred_listing'

    @Lazy
    def persons(self):
        self.setupController()
        for ch in self.context.getChildren([self.defaultPredicate]):
            if IQuestionnaire.providedBy(adapted(ch)):
                baseUrl = self.nodeView.getUrlForTarget(ch)
                break
        else:
            return [dict(title='Questionnaire missing')]
        me = getPersonForUser(self.context, self.request)
        result = [adapted(p) for p in self.institution.getChildren()
                             if p != me]
        result = [dict(title=p.title, 
                       url='%s?person=%s' % (baseUrl, p.uid)) 
                    for p in result if IPerson.providedBy(p)]
        return result


class JobAssignmentsForm(PersonView):
    """ Form for assigning jobs to a person.
    """

    macroName = 'jobassignmentsform'

    pageTitle = 'label_jobs_assigned'

    def getData(self):
        result = []
        assignments = self.jobAssignments()
        for job in self.jobs:
            checked = job in assignments['jobs']
            result.append(dict(title=job.title, uid=job.uid, checked=checked))
        return result

    def update(self):
        form = self.request.form
        if form.get('button_cancel'):
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return False
        if not form.get('submit_save'):
            return True
        current = self.jobAssignments()['jobs']
        newUids = form.get('assignments') or []
        for job in self.jobs:
            if job.uid in newUids:
                if job not in current:
                    self.context.assignParent(baseObject(job))
            else:
                if job in current:
                    self.context.deassignParent(baseObject(job))
        return True


class QualificationsForm(PersonView):
    """ Form for entering qualifications for a person.
    """

    macroName = 'qualificationsform'
    pageTitle = 'label_qualifications'
    textParentName = 'qualificationsrecorded'

    def getTitle(self):
        if not IPerson.providedBy(self.adapted):
            dummy = self.breadcrumbsParent  # evaluate before tweaking context
            self.context = getPersonForUser(self.context, self.request)
            self.adapted = adapted(self.context)
        return super(QualificationsForm, self).getTitle()

    def getData(self):
        self.setupController()
        self.registerDojoComboBox()
        form = self.request.form
        if form.get('button_cancel'):
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return []
        data = {}
        input = form.get('qualifications')
        for item in (input or []):
            data[item['key']] = item
        if data:
            self.update(data)
        else:
            qu = self.getQualifications(adapted(self.target))
            if qu is not None:
                data = qu.data
        result = []
        qualifications = self.conceptManager['qualifications']
        for obj in qualifications.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(obj)
            dataRow = data.get(uid) or {}
            item = dict(key=uid, label=obj.title, 
                        desc=obj.description,
                        certVocabulary=adapted(obj).certVocabulary or [],
                        subitems=[], schema=[],
                        value=dataRow.get('value') or (3 * [u'']),
                        cert=dataRow.get('cert') or (3 * [u'']))
            for subitem in obj.getChildren([self.defaultPredicate]):
                item['subitems'].append(dict(
                            uid=util.getUidForObject(subitem),
                            title=subitem.title))
            for row in adapted(obj).data.values():
                key = row[0]
                if len(row) < 6:
                    continue
                value = dataRow.get('qu_' + key) or (3 * [u''])
                item['schema'].append(dict(                            
                            key=key, label=row[1], 
                            level=row[2], type=row[4], 
                            vocabulary=row[5].split(';'),
                            value=value))
            result.append(item)
        return result

    def update(self, data):
        person = adapted(self.target)
        qu = self.getQualifications(person)
        if qu is None:
            qu = self.createQualifications(person)
        qu.data = data
        return self.processStateTransition(qu)

    def createQualifications(self, person):
        concepts = self.conceptManager
        name = 'qu.' + person.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['qualificationsrecorded']
        obj = addObject(concepts, Concept, name, type=type,
                        title='Qualifications: ' + person.title)
        baseObject(person).assignChild(obj)
        return adapted(obj)


class SkillsForm(QualificationsForm):
    """ Form for entering skills for a person.
    """

    macroName = 'skillsform'
    pageTitle = 'label_skills'
    textParentName = 'skillsrecorded'

    def getData(self):
        self.setupController()
        self.registerDojoComboBox()
        form = self.request.form
        if form.get('button_cancel'):
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return {}
        data = {}
        input = form.get('skills') or []
        for key in input:
            row = form.get('skills.' + key)
            if row['value']:
                if not data:
                    data = dict(value=[], exp=[], int=[])
                data['value'].append(row['value'])
                data['exp'].append(row['exp'])
                data['int'].append(row['int'])
        if data:
            self.update(data)
        else:
            sk = self.getSkills(adapted(self.target))
            if sk is not None:
                data = sk.data
        obj = self.conceptManager['skills']
        item = dict(subitems=[],
                    value=data.get('value') or [],
                    exp=data.get('exp') or [],
                    int=data.get('int') or [])
        fill(item['value'], u'', 15)
        fill(item['exp'], u'0', 15)
        fill(item['int'], u'0', 15)
        for subitem in obj.getChildren([self.defaultPredicate]):
            item['subitems'].append(dict(
                        uid=util.getUidForObject(subitem),
                        title=subitem.title))
        return item

    def update(self, data):
        person = adapted(self.target)
        qu = self.getSkills(person)
        if qu is None:
            qu = self.createSkills(person)
        qu.data = data
        return self.processStateTransition(qu)

    def createSkills(self, person):
        concepts = self.conceptManager
        name = 'sk.' + person.name
        name = INameChooser(concepts).chooseName(name, None)
        type = concepts['skillsrecorded']
        obj = addObject(concepts, Concept, name, type=type,
                        title='Skills: ' + person.title)
        baseObject(person).assignChild(obj)
        return adapted(obj)


def fill(lst, v, length):
    lst.extend((length - len(lst)) * [v])
