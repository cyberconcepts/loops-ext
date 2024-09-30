=============================
Knowledge Management Specials
=============================

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

  >>> from loops.tests.setup import TestSite
  >>> t = TestSite(site)
  >>> concepts, resources, views = t.setup()
  >>> loopsRoot = site['loops']

We then import a loops .dmp file containing all necessary types and
predicates.

  >>> from loops.knowledge.tests import importData
  >>> importData(loopsRoot)

  >>> from cyberapps.knowledge.tests import importData
  >>> importData(loopsRoot)


Job Positions
=============

Job positions, qualifications, interpersonal skills
---------------------------------------------------

  >>> from cyberapps.knowledge.browser.qualification import JobPositionsOverview
  >>> from cyberapps.knowledge.browser.qualification import IPSkillsForm

Person data
-----------

  >>> from cyberapps.knowledge.browser.person import JobPersonsOverview


Competences Questionnaire
=========================

  >>> from cyberapps.knowledge.data import IPSkillsQuestionnaire


Reporting
=========

  >>> from cyberapps.knowledge.browser.report import JobsListing, JobDescription

  