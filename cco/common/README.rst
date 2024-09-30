
cco.common - cyberconcepts.org: common stuff
============================================

Let's first do some common imports and initializations.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.api import getName

  >>> from logging import getLogger
  >>> log = getLogger('cco.common')

  >>> from loops.setup import addAndConfigureObject, addObject
  >>> from loops.concept import Concept

  >>> concepts = loopsRoot['concepts']
  >>> type_type = concepts['type']
  >>> type_topic = addAndConfigureObject(concepts, Concept, 'topic',
  ...     conceptType=type_type)
  >>> type_task = addAndConfigureObject(concepts, Concept, 'task',
  ...     conceptType=type_type)
  >>> home = loopsRoot['views']['home']

We now create the first basic objects...

