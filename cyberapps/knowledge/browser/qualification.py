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

Base classes, job position and requirements views.
"""

from copy import deepcopy
from zope import interface, component
from zope.app.container.interfaces import INameChooser
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope.traversing.api import getName

from cybertools.browser.action import actions
from cybertools.stateful.interfaces import IStateful
from loops.browser.action import DialogAction
from loops.browser.concept import ConceptView
from loops.common  import adapted, baseObject, generateNameFromTitle
from loops.concept import Concept
from loops.knowledge.browser import InstitutionMixin
from loops.organize.party import getPersonForUser
from loops.organize.personal import favorite
from loops.organize.personal.interfaces import IFavorites
from loops.security.common import checkPermission
from loops.setup import addObject
from loops import util
from cyberapps.knowledge.interfaces import _


template = ViewPageTemplateFile('qualification_macros.pt')


actions.register('createJobPosition', 'portlet', DialogAction,
        title=_(u'Create Job...'),
        description=_(u'Create a new job / position.'),
        viewName='create_concept.html',
        dialogName='createPosition',
        typeToken='.loops/concepts/jobposition',
        fixedType=True,
        innerForm='inner_concept_form.html',
        permission='loops.AssignAsParent',
)


class QualificationBaseView(InstitutionMixin):

    template = template
    templateName = 'knowledge.qualification'

    showInBreadcrumbs = True

    textKeys = ['1']        # should be overridden by subclass
    textParentName = None   # to be specified by subclass

    def setupController(self):
        cm = self.controller.macros
        cm.register('css', 
                    identifier='cyberapps.knowledge.css', 
                    resourceName='cyberapps.knowledge.css',
                    media='all', priority=90)

    def getTexts(self):
        result = {}
        if not self.textParentName:
            return result
        textKeys = self.textKeys
        parent = self.conceptManager[self.textParentName]
        for idx, r in enumerate(parent.getResources()[:len(textKeys)]):
            result[textKeys[idx]] = dict(
                    title=r.title, text=self.renderText(r.data, r.contentType))
        return result

    @Lazy
    def jobPositionType(self):
        return self.conceptManager['jobposition']

    def registerDojoSlider(self):
        self.registerDojo()
        jsCall = ('dojo.require("dijit.form.HorizontalSlider");'
                  'dojo.require("dijit.form.HorizontalRule");'
                  'dojo.require("dijit.form.HorizontalRuleLabels");')
        self.controller.macros.register('js-execute', 
                'dojo.require.HorizontalSlider', jsCall=jsCall)

    def registerDojoCharting(self):
        self.registerDojo()
        jsCall = ('dojo.require("dojox.charting.Chart");'
                  'dojo.require("dojox.charting.plot2d.ClusteredBars");'
                  'dojo.require("dojox.charting.themes.Claro");')
        self.controller.macros.register('js-execute', 
                'dojo.require.Charting', jsCall=jsCall)

    def processStateTransition(self, obj):
        stf = component.getAdapter(baseObject(obj), IStateful, 
                                   name='task_states')
        state = stf.state
        if self.request.form.get('submit_activate'):
            if state == 'draft':
                stf.doTransition('release')
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return False
        elif state == 'active':
            stf.doTransition('reopen')
        return True

    def createJob(self, title):
        concepts = self.conceptManager
        inst = self.institution
        #name = 'jobposition.%s_%s' % (
        #            getName(inst), generateNameFromTitle(title))
        name = 'jobposition.%s' % generateNameFromTitle(title)
        name = INameChooser(concepts).chooseName(name, None)
        obj = addObject(concepts, Concept, name, title=title,
                        type=self.jobPositionType)
        obj.assignParent(inst)
        return adapted(obj)


class JobPositionsOverview(QualificationBaseView, ConceptView):

    macroName = 'jobpositions'
    textParentName = 'data_entry'

    def update(self):
        form = self.request.form
        if form.get('create_jobposition'):
            title = form.get('form_jptitle')
            if not title:
            # TODO: provide error message
                return True
            job = self.createJob(title)
            return True
        instUid = form.get('select_institution')
        if instUid:
            return self.setInstitution(instUid)

    @Lazy
    def positions(self):
        result = []
        self.setupController()
        self.registerDojoComboBox()
        inst = baseObject(self.institution)
        if inst is not None:
            for child in inst.getChildren([self.defaultPredicate]):
                if child.conceptType == self.jobPositionType:
                    result.append(PositionView(child, self.request))
        return result

    @Lazy
    def jobTitles(self):
        table = self.conceptManager.get('job_names')
        if table is None:
            return []
        return [v[0] for v in adapted(table).data.values()]


class PositionView(QualificationBaseView, ConceptView):

    parentName = None

    @Lazy
    def breadcrumbsParent(self):
        parent = None
        if self.parentName is not None:
            parent = self.conceptManager.get(self.parentName)
        if parent is None:
            for p in self.context.conceptType.getParents([self.queryTargetPredicate]):
                parent = p
        return self.nodeView.getViewForTarget(parent)

    @Lazy
    def copyUrl(self):
        return '%s/copy_jpprofiles' % (self.nodeView.getUrlForTarget(self.context))

    @Lazy
    def deleteUrl(self):
        #for f in (self.jpDescription, self.ipskillsRequired, 
        #          self.qualificationsRequired):
        #    if f['state'] != 'none':
        #        return None
        return '%s/del_jobposition' % (self.nodeView.getUrlForTarget(self.context))

    @Lazy
    def jpDescription(self):
        jpDesc = adapted(self.target).getJPDescription()
        if jpDesc is None:
            state = 'none'
            text = 'to be done'
        else:
            stf = component.getAdapter(baseObject(jpDesc), IStateful, 
                                       name='task_states')
            state = stf.state
            text = stf.getStateObject().title
        action = 'edit_jpdescription.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        return dict(text=text, editUrl=editUrl, state=state)

    @Lazy
    def ipskillsRequired(self):
        ipsReq = adapted(self.target).getIPSkillsRequired()
        if ipsReq is None:
            state = 'none'
            text = 'to be done'
        else:
            stf = component.getAdapter(baseObject(ipsReq), IStateful, 
                                       name='task_states')
            state = stf.state
            text = stf.getStateObject().title
        action = 'edit_ipskillsreq.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        ipskillsUrl = None
        return dict(text=text, editUrl=editUrl, ipskillsUrl=ipskillsUrl, 
                    state=state)

    @Lazy
    def qualificationsRequired(self):
        quReq = adapted(self.target).getQualificationsRequired()
        if quReq is None:
            state = 'none'
            text = 'to be done'
        else:
            stf = component.getAdapter(baseObject(quReq), IStateful, 
                                       name='task_states')
            state = stf.state
            text = stf.getStateObject().title
        action = 'edit_qualificationsreq.html'
        editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        return dict(text=text, editUrl=editUrl, state=state)

    @Lazy
    def ipskills(self):
        #action = 'edit_ipskills.html'
        #editUrl = '%s/%s' % (self.nodeView.getUrlForTarget(self.context), action)
        ipskillsUrl = None
        return dict(text='to be done')  #, editUrl=editUrl, ipskillsUrl=ipskillsUrl)


class DeleteJobPosition(PositionView):

    isToplevel = True
    parentName = 'data_entry'
        
    def __call__(self):
        obj = self.adapted
        jobdesc = obj.getJPDescription()
        ipskills = obj.getIPSkillsRequired()
        qualif = obj.getQualificationsRequired()
        for subobj in (jobdesc, ipskills, qualif):
            if subobj is not None:
                name = getName(baseObject(subobj))
                del self.conceptManager[name]
        targetUrl = self.breadcrumbsParent.targetUrl
        name = getName(self.context)
        del self.conceptManager[name]
        return self.request.response.redirect(targetUrl)


class CopyJPProfiles(PositionView):

    isToplevel = True
    parentName = 'data_entry'
        
    def __call__(self):
        source = self.adapted
        jobdesc = source.getJPDescription()
        ipskills = source.getIPSkillsRequired()
        qualif = source.getQualificationsRequired()
        new = self.createJob(self.context.title)
        if jobdesc is not None:
            newJobdesc = new.createJPDescription()
            newJobdesc.header = deepcopy(jobdesc.header)
            newJobdesc.administrativeData = deepcopy(jobdesc.administrativeData)
            newJobdesc.workDescription = deepcopy(jobdesc.workDescription)
        if ipskills is not None:
            newIpskills = new.createIPSkillsRequired()
            newIpskills.requirements = deepcopy(ipskills.requirements)
        if qualif is not None:
            newQualif = new.createQualificationsRequired()
            newQualif.requirements = deepcopy(qualif.requirements)
        url = self.breadcrumbsParent.targetUrl
        return self.request.response.redirect(url)


class JPDescForm(PositionView):
    """ Form for entering job description for a certain position.
    """

    macroName = 'jpdescform'
    textKeys = ['administrative', 'workdesc', 'footer']
    textParentName = 'jpdescription'
    parentName = 'data_entry'

    def getData(self):
        self.setupController()
        self.registerDojoComboBox()
        result = dict(header={}, administrative=[], workdesc=[])
        jp = adapted(self.target)
        jpDesc = jp.getJPDescription()
        form = self.request.form
        if form.get('button_cancel'):
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return result
        data = dict(header={}, administrative={}, workdesc={})
        for k, v in (form.get('header') or {}).items():
            data['header'][k] = v
        for item in (form.get('administrative') or []):
            data['administrative'][item['key']] = item
        for item in (form.get('workdesc') or []):
            data['workdesc'][item['key']] = item
        if data['administrative']:
            self.update(data)
        elif jpDesc is not None:
            if jpDesc.administrativeData:
                data['administrative'] = jpDesc.administrativeData
            if jpDesc.workDescription:
                data['workdesc'] = jpDesc.workDescription
            if jpDesc.header:
                data['header'] = jpDesc.header
        titleData = data['administrative'].get('title')
        if not titleData or not titleData.get('text'):
            data['administrative']['title'] = dict(key='title', text=jp.title)
        result['header'] = data['header']
        adminDT = adapted(self.conceptManager['jpdesc_administrative'])
        for row in adminDT.data.values():
            if len(row) < 4:
                continue
            key, label, desc, optional = row
            dataRow = data['administrative'].get(key) or {}
            result['administrative'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or u'', 
                     inactive=dataRow.get('inactive')))
        workdescDT = adapted(self.conceptManager['jpdesc_workdesc'])
        for row in workdescDT.data.values():
            if len(row) < 4:
                continue
            key, label, desc, optional = row
            dataRow = data['workdesc'].get(key) or {}
            result['workdesc'].append(
                dict(key=key, label=label, desc=desc, optional=bool(optional),
                     text=dataRow.get('text') or (5 * [u'']), 
                     inactive=dataRow.get('inactive')))
        return result

    def update(self, data):
        jp = adapted(self.target)
        jobdesc = jp.getJPDescription()
        if jobdesc is None:
            jobdesc = jp.createJPDescription()
        jobdesc.header = data['header']
        jobdesc.administrativeData = data['administrative']
        titleData = data['administrative'].get('title')
        if titleData and titleData.get('text') != jp.title:
            jp.title = titleData['text']
        jobdesc.workDescription = data['workdesc']
        return self.processStateTransition(jobdesc)


class QualificationsForm(PositionView):
    """ Form for entering qualifications required for a certain position.
    """

    macroName = 'qualificationsform'
    textKeys = ['1', '2']
    textParentName = 'qualificationsrequired'
    parentName = 'data_entry'

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
            qureq = adapted(self.target).getQualificationsRequired()
            if qureq is not None:
                data = qureq.requirements
        result = []
        qualifications = self.conceptManager['qualifications']
        for obj in qualifications.getChildren([self.defaultPredicate]):
            uid = util.getUidForObject(obj)
            dataRow = data.get(uid) or {}
            item = dict(key=uid, label=obj.title, 
                        desc=obj.description,
                        subitems=[], schema=[],
                        value=dataRow.get('value') or (3 * [u'']),
                        req=dataRow.get('req') or (3 * [u'0']))
            for subitem in obj.getChildren([self.defaultPredicate]):
                item['subitems'].append(dict(
                            uid=util.getUidForObject(subitem),
                            title=subitem.title))
            for row in adapted(obj).data.values():
                if len(row) < 6:
                    continue
                key = row[0]
                value = dataRow.get('qu_' + key) or (3 * [u''])
                item['schema'].append(dict(                            
                            key=key, label=row[1], 
                            level=row[2], type=row[4], 
                            vocabulary=row[5].split(';'),
                            value=value))
            result.append(item)
        return result

    def update(self, data):
        jp = adapted(self.target)
        qureq = jp.getQualificationsRequired()
        if qureq is None:
            qureq = jp.createQualificationsRequired()
        qureq.requirements = data
        return self.processStateTransition(qureq)


class IPSkillsForm(PositionView):
    """ Form for entering interpersonal skills required for a certain position.
    """

    macroName = 'ipskillsform'
    textKeys = ['1', '2']
    textParentName = 'ipskillsrequired'
    parentName = 'data_entry'

    numberSelected = 0

    def getData(self):
        self.setupController()
        form = self.request.form
        if form.get('button_cancel'):
            url = self.breadcrumbsParent.targetUrl
            self.request.response.redirect(url)
            return []
        data = {}
        input = form.get('ipskills')
        for item in (input or []):
            data[item['uid']] = item
        self.registerDojoSlider()
        if data:
            self.update(data)
        else:
            skillsreq = adapted(self.target).getIPSkillsRequired()
            if skillsreq is not None:
                data = skillsreq.requirements
        result = []
        ipskills = self.conceptManager['ipskills']
        for parent in ipskills.getChildren([self.defaultPredicate]):
            #toplevelSkill = adapted(parent)
            uid = util.getUidForObject(parent)
            item = dict(uid=uid, label=parent.title, 
                        description=parent.description, skills=[])
            for child in parent.getChildren([self.defaultPredicate]):
                #skill = adapted(child)
                uid = util.getUidForObject(child)
                row = data.get(uid) or {}
                selected = row.get('selected')
                if selected:
                    self.numberSelected += 1
                item['skills'].append(
                    dict(uid=uid, label=child.title,
                         description=child.description,
                         selected=row.get('selected'),
                         expected=row.get('expected') or 0))
            result.append(item)
        return result

    def update(self, data):
        jp = adapted(self.target)
        skillsreq = jp.getIPSkillsRequired()
        if skillsreq is None:
            skillsreq = jp.createIPSkillsRequired()
        skillsreq.requirements = data
        return self.processStateTransition(skillsreq)

