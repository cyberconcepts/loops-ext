#! /usr/bin/python

"""
Tests for the 'cco.work' package.
"""

import os
import unittest, doctest
from zope import component
from zope.app.testing.setup import placefulSetUp, placefulTearDown

from cybertools.organize.work import workItemStates
from cybertools.tracking.btree import TrackingStorage
from loops.concept import Concept
from loops.expert.report import IReport, IReportInstance, Report
from loops.organize.work.base import WorkItem, WorkItems
from loops.setup import addAndConfigureObject
from loops.tests.setup import TestSite
from cco.work.interfaces import IProject, ITask
from cco.work.report import TasksOverview
from cco.work.task import Project, Task


def setupComponents(loopsRoot):
    component.provideAdapter(WorkItems)
    component.provideUtility(workItemStates(), name='organize.workItemStates')
    component.provideAdapter(Project)
    component.provideAdapter(Report, provides=IReport)
    component.provideAdapter(Task)
    component.provideAdapter(TasksOverview, provides=IReportInstance,
                             name='cco.work.tasks_overview')


def setUp(self):
    site = placefulSetUp(True)
    t = TestSite(site)
    concepts, resources, views = t.setup()
    loopsRoot = site['loops']
    self.globs['loopsRoot'] = loopsRoot
    setupComponents(loopsRoot)
    records = loopsRoot.getRecordManager()
    if 'work' not in records:
        records['work'] = TrackingStorage(trackFactory=WorkItem)
    setupObjects(concepts)

def setupObjects(concepts):
    addAndConfigureObject(concepts, Concept, 'project',
            title='Project', conceptType=concepts['type'],
            typeInterface=IProject)
    addAndConfigureObject(concepts, Concept, 'task',
            title='Task', conceptType=concepts['type'],
            typeInterface=ITask)
    addAndConfigureObject(concepts, Concept, 'report',
            title='Task', conceptType=concepts['type'],
            typeInterface=IReport)
    addAndConfigureObject(concepts, Concept, 'tasks_overview',
            title='Tasks Overview', conceptType=concepts['report'],
            reportType='cco.work.tasks_overview')


def tearDown(self):
    placefulTearDown()


class StorageTest(unittest.TestCase):
    "Basic tests."

    def setUp(self):
        site = placefulSetUp(True)
        t = TestSite(site)
        self.concepts, resources, views = t.setup()
        loopsRoot = site['loops']
        setupComponents(loopsRoot)
        setupObjects(self.concepts)

    def tearDown(self):
        placefulTearDown()

    def testStorage(self):
        self.setUp()        
        #print('***', self.concepts)
        self.tearDown()


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    loader = unittest.TestLoader()
    return unittest.TestSuite((
        doctest.DocFileSuite('README.rst', optionflags=flags,
                     setUp=setUp, tearDown=tearDown),
        loader.loadTestsFromTestCase(StorageTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
