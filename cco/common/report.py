# cco.common.report

""" Common classes and other definitions for reporting.
"""

from datetime import datetime
import json

from zope.cachedescriptors.property import Lazy
from zope.dublincore.interfaces import IZopeDublinCore
from zope.i18n import translate

from cybertools.browser.action import actions
from cybertools.composer.report.base import operators as base_operators
from cybertools.composer.report.result import Row as BaseRow
from cybertools.util.date import date2TimeStamp
from loops.common import adapted, baseObject, AdapterBase
from loops.expert.field import Field, UrlField as BaseUrlField,\
    DateField as BaseDateField, IntegerField as BaseIntegerField,\
    DecimalField as BaseDecimalField, RelationField as BaseRelationField,\
    VocabularyField as BaseVocabularyField
from loops.expert.report import ReportInstance as BaseReportInstance
from loops.organize.party import getPersonForUser
from loops.util import getUidForObject

from cco.common.util import _, parseNumber, json_serial


class RelationField(BaseRelationField):

    def getValue(self, row):
        value = self.getRawValue(row)
        if not value:
            return
        return getattr(value, self.displayAttribute)

    def getSelectValue(self, row):
        return self.getRawValue(row)

    def getSortValue(self, row):
        return self.getValue(row)

    def getExportValue(self, row, format=''):
        return self.getValue(row)

    def getDisplayValue(self, row):
        value = self.getRawValue(row)
        if not value:
            return dict(title=u'', url=u'')
        nv = row.parent.context.view.nodeView
        return dict(title=getattr(value, self.displayAttribute),
                    url=nv.getUrlForTarget(baseObject(value)))


class DecimalField(BaseDecimalField):

    pass


class DateField(BaseDateField):

    def getExportValue(self, row, format='csv'):
        val = super(DateField, self).getExportValue(row, format=format)
        if not val:
            val = None
        return val

    def getSortValue(self, row):
        value = self.getRawValue(row)
        if value is not None:
            value = date2TimeStamp(value)
            if getattr(self, 'sortDesc', False):
                value = -value
        return value


class IntegerField(BaseIntegerField):

    def getSortValue(self, row):
        value = self.getRawValue(row)
        if value is not None:
            if getattr(self, 'sortDesc', False):
                value = -value
        return value


class UrlField(BaseUrlField):

    def getDisplayValue(self, row):
        contextAttr = getattr(self, 'contextAttr', 'item') or 'item'
        context = getattr(row, contextAttr, None) or row.context
        if not isinstance(context, AdapterBase):
            return dict(title=self.getValue(row), url=u'')
        nv = row.parent.context.view.nodeView
        return dict(title=self.getValue(row),
                    url=nv.getUrlForTarget(baseObject(context)))


class CurrencyField(BaseDecimalField):

    def getRawValue(self, row):
        value = row.getRawValue(self.name)
        if value:
            if isinstance(value, str):
                value = parseNumber(value)
            if not isinstance(value, float):
                value = float(value)
        return value


class MenuField(Field):

    template = None
    renderer = 'menu'

    def getValue(self, row):
        return self.getRawValue(row) or []

    def getDisplayValue(self, row):
        result = []
        if row.context is not None:
            values = self.getValue(row)
            result = actions.get(view=row.parent.context.view,
                                 page=row.parent.context.view.nodeView,
                                 target=row.context,
                                 names=values)
        return result


class VocabularyField(BaseVocabularyField):

    def getExportValue(self, row, format=None, lang=None):
        return self.getDisplayValue(row)


objectActions = MenuField(
    'actions',
    _(u'Actions'),
    executionSteps=['output', 'actions'])

identifier = UrlField(
    'identifier',
    u'ID',
    description=u'',
    executionSteps=['sort', 'output'])

comments = Field(
    'comments',
    u'Last Comments',
    cssClass='width-auto',
    executionSteps=['output'])

description = UrlField(
    'description',
    _(u'Description'),
    dbtype='string',
    cssClass='width-auto',
    executionSteps=['sort', 'output'])

longTitle = UrlField(
    'longTitle',
    _('label_longTitle'),
    dbtype='string',
    executionSteps=['sort', 'output'])

modificationDate = DateField(
    'modificationDate',
    u'modificationDate',
    description=u'',
    executionSteps=['output', 'sort'])

creationDate = DateField(
    'creationDate',
    _(u'label_creationDate'),
    description=u'',
    executionSteps=['output', 'sort'])

currentDate = DateField(
    'currentDate',
    u'label_currentDate',
    description=u'label_currentDate',
    executionSteps=(['output']))

titleQuery = Field(
    'titleQuery',
    _('Title'),
    operator='substring',
    executionSteps=['query'])

identifierQuery = Field(
    'identifierQuery',
    _('label_identifier'),
    operator='substring',
    executionSteps=['query'])


class Row(BaseRow):

    cssClass = 'row'

    @Lazy
    def uid(self):
        return getUidForObject(baseObject(self.context))

    @Lazy
    def currentDate(self):
        return datetime.now()

    @Lazy
    def modificationDate(self):
        dc = IZopeDublinCore(baseObject(self.context), None)
        if dc is not None:
            return dc.modified

    @Lazy
    def creationDate(self):
        dc = IZopeDublinCore(baseObject(self.context), None)
        if dc is not None:
            return dc.created

    @Lazy
    def currentPerson(self):
        person = getPersonForUser(self.parent.context.view.context,
                                  self.parent.context.view.request)
        if person is not None:
            return adapted(person)

    @Lazy
    def identifierQuery(self):
        return self.context.identifier

    @Lazy
    def titleQuery(self):
        return self.context.title

    @Lazy
    def actions(self):
        return ['edit_concept', 'info']

    def useRowProperty(self, attr):
        return getattr(self, attr)

    attributeHandlers = dict(
        identifierQuery=useRowProperty,
        modificationDate=useRowProperty,
        creationDate=useRowProperty,
        sequenceNumber=useRowProperty,
        actions=useRowProperty,
        uid=useRowProperty,
        titleQuery=useRowProperty)


class TrackRow(Row):

    @staticmethod
    def getContextAttr(obj, attr):
        if attr in obj.context.metadata_attributes:
            return getattr(obj.context, attr)
        return obj.context.data.get(attr)


def checkEqual(value, compValue):
    return value == compValue


def checkSubString(value, compValue):
    return compValue.lower() in value.lower()


def checkTrue(value, compValue):
    return True


def checkAbsoluteValue(value, compValue):
    if not value:
        value = 0.0
    if abs(float(value)) == abs(parseNumber(compValue)):
        return True
    return False


def checkAbsoluteInValue(value, compValue):
    for val in value:
        if abs(float(val)) == abs(parseNumber(compValue)):
            return True
    return False


def checkAnyEqual(value, compValue):
    if not compValue or not value:
        return False
    return compValue in value


def checkLessOrEqual(value, compValue):
    if value and compValue:
        return int(value) <= int(compValue)
    return False


def checkGreaterOrEqual(value, compValue):
    if value and compValue:
        return int(value) >= int(compValue)
    return False


operators = base_operators.update({'equal': checkEqual,
                                   'substring': checkSubString,
                                   'true': checkTrue,
                                   # 'ge': checkGreaterOrEqual,
                                   # 'le': checkLessOrEqual,
                                   'anyequal': checkAnyEqual,
                                   'absolute': checkAbsoluteValue,
                                   'absolutein': checkAbsoluteInValue})


class ReportInstance(BaseReportInstance):

    rowFactory = Row
    userSettings = None
    rowTransitions = None
    balanceData = None
    dataTableExtraTotals = []
    resultMacros = dict()

    def getDataTableFieldClass(self, field):
        if field.cssClass and 'default' not in field.cssClass:
            return 'default %s' % field.cssClass
        return field.cssClass or 'default'

    def getEditFields(self):
        return [f for f in self.fields if 'edit' in f.executionSteps]

    def calculateTotals(self, suffix='', res=None):
        if res is None:
            res = self.getResults()
        data = res.totals.data
        for f in self.getTotalsFields():
            if getattr(f, 'totalsMethod', 'row') == 'instance':
                value = f.getTotalsValue(self, suffix=suffix) or 0.0
                if value:
                    data[f.name] = round(value, 2)
            else:
                for row in res:
                    value = f.getRawValue(row) or 0.0
                    if value:
                        data[f.name] = data.get(f.name, 0.00) + round(value, 2)
        return data

    @Lazy
    def jsonFieldLayout(self):
        result = [dict(field=field.name,
                       name=translate(_(field.title),
                                      target_language='de'),
                       width=getattr(field, 'width', '125px'),
                       editable=False,
                       styles='number' in getattr(field, 'cssClass', '') and
                       'text-align:right;' or None,
                       formatter='format' + ''.join(list(
                           getattr(field, 'format', 'field'))).title())
                  for field in self.view.displayedColumns]
        return json.dumps(result)

    @Lazy
    def jsonDataList(self):
        result = []
        for row in self.view.results():
            data = dict()
            for idx, col in enumerate(row.displayedColumns):
                data[col.name] = col.getRawValue(row)
            result.append(data)
        return json.dumps(result, default=json_serial)

    def getResultsRenderer(self, name, macros):
        return self.resultMacros.get(name, macros[name])


class DataTableRow(Row):

    @Lazy
    def dataTable(self):
        return self.parent.context.dataTable

    def getRawValue(self, attr):
        index = self.dataTable.getColumns().index(attr)
        if index:
            return self.context[index-1]
