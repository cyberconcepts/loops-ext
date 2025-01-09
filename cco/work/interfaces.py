# cco.work.interfaces 

""" Interfaces for organizational stuff like persons and addresses.
"""

from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope import interface, component, schema

from cybertools.composer.schema.field import FieldInstance
from cybertools.composer.schema.interfaces import FieldType
from cybertools.organize.interfaces import ITask
from loops.interfaces import ILoopsAdapter, IConceptSchema


_ = MessageFactory('cco.work')



class Duration(schema.Int):

    __typeInfo__ = ('duration',
                    FieldType('textline',
                              u'A field representing a duration in time.',
                              instanceName='duration'))


class DurationFieldInstance(FieldInstance):

    def display(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            value = value.replace(',', '.')
        try:
            value = float(value)
        except ValueError:
            value = 0.0
        return u'%02i:%02i' % divmod(value * self.factor / 60.0, 60)

    @property
    def factor(self):
        return getattr(self.context.baseField, 'factor', 1)    


# project and task management

class IProject(ILoopsAdapter):

    estimatedEffort = Duration(
                title=_(u'label_estimatedEffort'),
                description=_(u'desc_estimatedEffort'),
                readonly=True,)
    chargedEffort = Duration(
                title=_(u'label_chargedEffort'),
                description=_(u'desc_chargedEffort'),
                readonly=True,)
    actualEffort = Duration(
                title=_(u'label_actualEffort'),
                description=_(u'desc_actualEffort'),
                readonly=True)

    estimatedEffort.factor = chargedEffort.factor = 3600


class ITask(IConceptSchema, ITask, IProject):

    estimatedEffort = Duration(
                title=_(u'label_estimatedEffort'),
                description=_(u'desc_estimatedEffort'),
                required=False,)
    chargedEffort = Duration(
                title=_(u'label_chargedEffort'),
                description=_(u'desc_chargedEffort'),
                required=False,)

    estimatedEffort.factor = chargedEffort.factor = 3600

