##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object Copier Tests
"""
import doctest
import unittest

import zope.component
from zope.component.eventtesting import clearEvents
from zope.component.eventtesting import getEvents
from zope.container import testing
from zope.traversing.api import traverse

from zope.copypastemove import ObjectCopier
from zope.copypastemove.interfaces import IObjectCopier


class File:
    pass


def test_copy_events():
    """
    Prepare an IObjectCopier::

      >>> from zope import component
      >>> component.provideAdapter(ObjectCopier, (None,), IObjectCopier)

    We set things up in a root folder::

      >>> from zope.container.sample import SampleContainer
      >>> root = SampleContainer()

    Prepare some objects::

      >>> folder = SampleContainer()
      >>> root['foo'] = File()
      >>> root['folder'] = folder
      >>> list(folder.keys())
      []
      >>> foo = traverse(root, 'foo') # wrap in ContainedProxy

    Now make a copy::

      >>> clearEvents()
      >>> copier = IObjectCopier(foo)
      >>> copier.copyTo(folder, 'bar')
      'bar'

    Check that the copy has been done::

      >>> list(folder.keys())
      ['bar']

    Check what events have been sent::

      >>> events = getEvents()
      >>> [event.__class__.__name__ for event in events]
      ['ObjectCopiedEvent', 'ObjectAddedEvent', 'ContainerModifiedEvent']

    Check that the ObjectCopiedEvent includes the correct data::

      >>> events[0].object is folder['bar']
      True
      >>> events[0].original is root['foo']
      True
    """


class ObjectCopierTest(testing.ContainerPlacefulSetup, unittest.TestCase):

    def setUp(self):
        testing.ContainerPlacefulSetup.setUp(self)
        self.buildFolders()
        zope.component.provideAdapter(ObjectCopier, (None,), IObjectCopier)

    def test_copytosame(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(container, 'file1')
        self.assertIn('file1', container)
        self.assertIn('file1-2', container)

    def test_copytosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(container, 'file2')
        self.assertIn('file1', container)
        self.assertIn('file2', container)

    def test_copytoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file1')
        self.assertIn('file1', container)
        self.assertIn('file1', target)

    def test_copytootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file2')
        self.assertIn('file1', container)
        self.assertIn('file2', target)

    def test_copytootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        target['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file1')
        # we do it twice, just to test auto-name generation
        copier.copyTo(target, 'file1')
        self.assertIn('file1', container)
        self.assertIn('file1', target)
        self.assertIn('file1-2', target)
        self.assertIn('file1-3', target)

    def test_copyable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        self.assertTrue(copier.copyable())

    def test_copyableTo(self):
        #  A file should be copyable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        self.assertTrue(copier.copyableTo(container, 'file1'))

    def test_copyfoldertosibling(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1/folder1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.assertIn('folder1_1', target)

    def test_copyfoldertosame(self):
        root = self.rootFolder
        target = traverse(root, '/folder1')
        source = traverse(root, '/folder1/folder1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.assertIn('folder1_1', target)

    def test_copyfoldertosame2(self):
        root = self.rootFolder
        target = traverse(root, '/folder1/folder1_1')
        source = traverse(root, '/folder1/folder1_1/folder1_1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.assertIn('folder1_1_1', target)

    def test_copyfolderfromroot(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.assertIn('folder1', target)

    def test_copyfolderfromroot2(self):
        root = self.rootFolder
        target = traverse(root, '/folder2/folder2_1/folder2_1_1')
        source = traverse(root, '/folder1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.assertIn('folder1', target)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(ObjectCopierTest),
        doctest.DocTestSuite(
            setUp=testing.ContainerPlacefulSetup().setUp,
            tearDown=testing.ContainerPlacefulSetup().tearDown),
    ))
