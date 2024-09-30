
cco.schema - cyberconcepts.org: controlling schema/form appearance
==================================================================

  >>> from zope.publisher.browser import TestRequest
  >>> from logging import getLogger
  >>> log = getLogger('cco.schema')

  >>> from loops.setup import addAndConfigureObject, addObject
  >>> from loops.concept import Concept
  >>> from loops.common import adapted

  >>> from loops.knowledge.tests import importData
  >>> importData(loopsRoot)

  >>> concepts = loopsRoot['concepts']

  >>> from loops.browser.node import NodeView
  >>> home = loopsRoot['views']['home']
  >>> homeView = NodeView(home, TestRequest())


Schema Controller
-----------------

### Type-controlled schemas ###

  >>> from cco.schema.base import SchemaController

  >>> from cco.schema.processor import SchemaProcessor


Special Fields
--------------

  >>> from cco.schema.field import UrlField, UrlFieldInstance
