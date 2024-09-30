# cco.schema.processor

""" Schema processor.
"""

from logging import getLogger
from zope.component import adapts
from zope.interface import implementer
from zope.traversing.api import getName

from cco.schema.interfaces import ISchemaController
from cybertools.composer.schema.interfaces import ISchemaFactory, ISchemaProcessor
from loops.browser.common import BaseView
from loops.common import adapted, baseObject


@implementer(ISchemaProcessor)
class SchemaProcessor(object):

    adapts(ISchemaFactory)

    logger = getLogger('cco.schema.SchemaProcessor')
    view = None

    def __init__(self, context):
        self.schemaFactory = context
        self.adapted = context.context
        self.schemaData = {}

    def setup(self, view, **kw):
        self.view = view
        self.schemaControllers = []
        typeToken = getattr(self.view, 'typeToken', None)
        if typeToken is None:
            if (getattr(self.adapted, '__is_dummy__', True) or 
                getName(baseObject(self.adapted)) is None):
                return
            self.type = baseObject(self.adapted).getType()
        else:
            self.type = view.loopsRoot.loopsTraverse(typeToken)
        opts = view.typeOptions('schema_controller')
        if opts:
            for opt in opts:
                data = opt.split('.')
                if data[0] not in self.scsetup:
                    self.logger.warn('unknown schema controller: %s.' % data[0])
                    return
                setupSctype = self.scsetup[data[0]]
                params = data[1:]
                setupSctype(self, params)

    def setupSchemaData(self, sd):
        for row in sd:
            row = dict(row)     # copy to avoid changing original data
            key = row.pop('fieldName', None)
            if not key:
                self.logger.warn('Empty field name in schema controller: %s.'
                                 % getName(c))
                continue
            if key in self.schemaData:
                self.logger.warn('Duplicate field name: %s.' % key)
            else:
                self.schemaData[key] = row

    def setupParentBasedSchemaController(self, params):
        if self.adapted.__is_dummy__:
            return      # there are no parents during object creation
        self.logger.debug('Parent-based, params: %s.' % params)
        if len(params) < 2:
            self.logger.warn(
                'Parent-based schema controller needs at least 2 parameters. '
                'Given: %s' % params)
            return
        predNames = params[0].split('/')
        typeName = params[1]
        recursive = 'recursive' in params[2:]
        predicate = self.view.conceptManager.get(predNames[0])
        if predicate is None:
            self.logger.warn('Predicate %s not found.' % predNames[0])
            return
        type = self.view.conceptManager.get(typeName)
        if type is None:
            self.logger.warn('Type %s not found.' % typeName)
            return
        uppreds = []
        for pn in predNames[1:]:
            uppred = self.view.conceptManager.get(pn)
            if uppred is None:
                self.logger.warn('Predicate %s not found.' % predNames[0])
            else:
                uppreds.append(uppred)
        self.setupParents(baseObject(self.adapted), 
                          predicate, type, recursive, uppreds=uppreds)

    def setupParents(self, obj, predicate, type, recursive, uppreds=[]):
        for c in obj.getParents([predicate]):
            if c.conceptType != type:
                continue
            adp = adapted(c)
            if not ISchemaController.providedBy(adp):
                self.logger.warn('No valid schema controller: %s.' % getName(c))
                continue
            sd = adp.schemaData
            if sd:
                self.logger.debug('Using schema controller %s.' % getName(c))
                self.setupSchemaData(sd)
            if recursive:
                if uppreds:
                    predicate = uppreds[0]
                    self.setupParents(c, predicate, type, recursive, uppreds[1:])
                else:
                    self.setupParents(c, predicate, type, recursive)

    def setupTypeBasedSchemaController(self, params):
        self.logger.debug('Type-based, params: %s.' % params)
        predName = 'use_schema'
        if params:
            predName = params[0]
        predicate = self.view.conceptManager.get(predName)
        if predicate is None:
            self.logger.warn('Predicate %s not found.' % predicateName)
            return
        for c in self.type.getParents([predicate]):
            adp = adapted(c)
            if not ISchemaController.providedBy(adp):
                self.logger.warn('No valid schema controller: %s.' % getName(c))
                return
            self.setupSchemaData(adp.schemaData)

    scsetup = dict(parent=setupParentBasedSchemaController,
                   type=setupTypeBasedSchemaController)

    def process(self, field, **kw):
        if self.view is None:
            view = kw.pop('manager', None)
            if isinstance(view, BaseView):
                self.setup(view, **kw)
            else:
                return field
        cinfo = self.schemaData.get(field.name)
        if cinfo is not None:
            self.processRequired(field, cinfo.get('required'))
            self.processEditable(field, cinfo.get('editable'))
            self.processDisplay(field, cinfo.get('display'))
        return field

    def processRequired(self, field, setting):
        if setting:
            field.required = setting == 'required'

    def processEditable(self, field, setting):
        if setting:
            field.readonly = setting == 'hidden'

    def processDisplay(self, field, setting):
        if setting:
            field.visible = setting == 'visible'

