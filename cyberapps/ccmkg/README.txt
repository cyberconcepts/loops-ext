=======================
CyberConcepts Marketing
=======================


Note: This package depends on loops.

Let's do some basic set up

  >>> from zope.app.testing.setup import placefulSetUp, placefulTearDown
  >>> site = placefulSetUp(True)

  >>> from zope import component, interface

and setup a simple loops site with a concept manager and some concepts
(with all the type machinery, what in real life is done via standard
ZCML setup):

  >>> from loops.interfaces import ILoops, IConcept
  >>> from loops.concept import Concept
  >>> from loops.setup import ISetupManager

from loops.knowledge.setup import SetupManager
component.provideAdapter(SetupManager, (ILoops,), ISetupManager,
                         name='knowledge')

  >>> from loops.tests.setup import TestSite
  >>> t = TestSite(site)
  >>> concepts, resources, views = t.setup()


Project References
==================

  >>> from cyberapps.ccmkg.interfaces import IProjectReference
  >>> from cyberapps.ccmkg.data import ProjectReferenceAdapter
  >>> component.provideAdapter(ProjectReferenceAdapter)
  >>> typeConcept = concepts.getTypeConcept()
  >>> from loops.setup import addAndConfigureObject

We can now create the project reference concept type...

  >>> tProjRef = addAndConfigureObject(concepts, Concept, 'projectreference',
  ...               title=u'Project Reference', conceptType=typeConcept,
  ...               typeInterface=IProjectReference)

... and a few projectreferences.

  >>> ref1 = addAndConfigureObject(concepts, Concept, 'ref1',
  ...               title=u'Reference #1', conceptType=tProjRef,
  ...               timeRange=u'2006-06', task=u'Development',
  ...               customerInfo=u'Goggle Inc', technology=u'Zope 3')
  >>> ref2 = addAndConfigureObject(concepts, Concept, 'ref2',
  ...               title=u'Reference #2', conceptType=tProjRef,
  ...               timeRange=u'2007-01 to 2007-04', task=u'Development',
  ...               customerInfo=u'San Narciso College', technology=u'Python')
  >>> ref3 = addAndConfigureObject(concepts, Concept, 'ref3',
  ...               title=u'Reference #3', conceptType=tProjRef,
  ...               timeRange=u'2007-01 to 2007-05', task=u'Consulting',
  ...               customerInfo=u'MASA', technology=u'Linux')

The Project Listing view
------------------------

  >>> from cybertools.reporter.resultset import ContentRow
  >>> from cybertools.reporter.interfaces import IRow
  >>> component.provideAdapter(ContentRow, provides=IRow)

  >>> from cyberapps.ccmkg.browser import ProjectListing
  >>> from zope.publisher.browser import TestRequest
  >>> from loops.view import Node

  >>> node = views['n1'] = Node()
  >>> node.target = tProjRef

  >>> #view = ProjectListing(node, TestRequest())
  >>> view = ProjectListing(tProjRef, TestRequest())

  >>> rs = view.resultSet
  >>> rows = list(rs.getRows())
  >>> for r in rows:
  ...     data = r.applyTemplate()
  ...     print(data['title'], data['timeRange'], data['customerInfo'])
  Reference #3 2007-01 to 2007-05 MASA
  Reference #2 2007-01 to 2007-04 San Narciso College
  Reference #1 2006-06 Goggle Inc
