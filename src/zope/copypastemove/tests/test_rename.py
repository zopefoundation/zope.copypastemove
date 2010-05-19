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
"""Test renaming of components

$Id$
"""
import unittest

from doctest import DocTestSuite
from zope.component import testing, eventtesting, provideAdapter, adapts
from zope.container.testing import PlacelessSetup, ContainerPlacefulSetup
from zope.copypastemove import ContainerItemRenamer, ObjectMover
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.container.contained import Contained, NameChooser
from zope.container.sample import SampleContainer

class TestContainer(SampleContainer):
    pass

class ObstinateNameChooser(NameChooser):
    adapts(TestContainer)

    def chooseName(self, name, ob):
        return u'foobar'

class RenamerTest(ContainerPlacefulSetup, unittest.TestCase):

    def setUp(self):
        ContainerPlacefulSetup.setUp(self)
        provideAdapter(ObjectMover)
        provideAdapter(ContainerItemRenamer)
        provideAdapter(ObstinateNameChooser)

    def test_obstinatenamechooser(self):
        container = TestContainer()
        container[u'foobar'] = Contained()
        renamer = IContainerItemRenamer(container)

        renamer.renameItem(u'foobar', u'newname')
        self.assertEqual(list(container), [u'foobar'])

container_setup = PlacelessSetup()

def setUp(test):
    testing.setUp()
    eventtesting.setUp()
    container_setup.setUp()

def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(RenamerTest),
            DocTestSuite('zope.copypastemove',
                         setUp=setUp, tearDown=testing.tearDown),
            ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
