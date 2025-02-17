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
"""Object Mover Tests
"""
import doctest
import unittest

import zope.component
from zope.component.eventtesting import clearEvents
from zope.component.eventtesting import getEvents
from zope.container import testing
from zope.traversing.api import traverse

from zope.copypastemove import ObjectMover
from zope.copypastemove.interfaces import IObjectMover


class File:
    pass


def test_move_events():
    """
    We need a root folder::

      >>> from zope.container.sample import SampleContainer
      >>> root = SampleContainer()

    Prepare the setup::

      >>> from zope import component
      >>> component.provideAdapter(ObjectMover, (None,), IObjectMover)

    Prepare some objects::

      >>> folder = SampleContainer()
      >>> root['foo'] = File()
      >>> root['folder'] = folder
      >>> list(folder.keys())
      []
      >>> foo = traverse(root, 'foo') # wrap in ContainedProxy

    Now move it::

      >>> clearEvents()
      >>> mover = IObjectMover(foo)
      >>> mover.moveableTo(folder)
      True
      >>> mover.moveTo(folder, 'bar')
      'bar'

    Check that the move has been done::

      >>> list(root.keys())
      ['folder']
      >>> list(folder.keys())
      ['bar']

    Check what events have been sent::

      >>> events = getEvents()
      >>> [event.__class__.__name__ for event in events]
      ['ObjectMovedEvent', 'ContainerModifiedEvent', 'ContainerModifiedEvent']

    Verify that the ObjectMovedEvent includes the correct data::

      >>> events[0].oldName, events[0].newName
      ('foo', 'bar')
      >>> events[0].oldParent is root
      True
      >>> events[0].newParent is folder
      True

    Let's look the other events:

      >>> events[1].object is folder
      True
      >>> events[2].object is root
      True

    """


class ObjectMoverTest(testing.ContainerPlacefulSetup, unittest.TestCase):

    def setUp(self):
        testing.ContainerPlacefulSetup.setUp(self)
        self.buildFolders()
        zope.component.provideAdapter(ObjectMover, (None,), )

    def test_movetosame(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(container, 'file1')
        self.assertIn('file1', container)
        self.assertEqual(len(container), 2)

    def test_movetosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(container, 'file2')
        self.assertNotIn('file1', container)
        self.assertIn('file2', container)

    def test_movetoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file1')
        self.assertNotIn('file1', container)
        self.assertIn('file1', target)

    def test_movetootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file2')
        self.assertNotIn('file1', container)
        self.assertIn('file2', target)

    def test_movetootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        target['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file1')
        self.assertNotIn('file1', container)
        self.assertIn('file1', target)
        self.assertIn('file1-2', target)

    def test_moveable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        self.assertTrue(mover.moveable())

    def test_moveableTo(self):
        #  A file should be moveable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        self.assertTrue(mover.moveableTo(container, 'file1'))

    def test_movefoldertosibling(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1/folder1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.assertIn('folder1_1', target)

    def test_movefoldertosame(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        target = traverse(root, '/folder1')
        source = traverse(root, '/folder1/folder1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.assertIn('folder1_1', target)
        self.assertEqual(len(target), 1)

    def test_movefoldertosame2(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        target = traverse(root, '/folder1/folder1_1')
        source = traverse(root, '/folder1/folder1_1/folder1_1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.assertIn('folder1_1_1', target)
        self.assertEqual(len(target), 1)

    def test_movefolderfromroot(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.assertIn('folder1', target)

    def test_movefolderfromroot2(self):
        root = self.rootFolder
        target = traverse(root, '/folder2/folder2_1/folder2_1_1')
        source = traverse(root, '/folder1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.assertIn('folder1', target)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(ObjectMoverTest),
        doctest.DocTestSuite(
            setUp=testing.ContainerPlacefulSetup().setUp,
            tearDown=testing.ContainerPlacefulSetup().tearDown),
    ))
