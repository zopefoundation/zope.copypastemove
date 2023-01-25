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
"""
import doctest
import unittest

from zope.component import adapter
from zope.component import eventtesting
from zope.component import provideAdapter
from zope.component import testing
from zope.container.contained import Contained
from zope.container.contained import NameChooser
from zope.container.sample import SampleContainer
from zope.container.testing import ContainerPlacefulSetup
from zope.container.testing import PlacelessSetup

from zope.copypastemove import ContainerItemRenamer
from zope.copypastemove import ObjectMover
from zope.copypastemove.interfaces import IContainerItemRenamer


class TestContainer(SampleContainer):
    pass


@adapter(TestContainer)
class ObstinateNameChooser(NameChooser):

    def chooseName(self, name, ob):
        return 'foobar'


class RenamerTest(ContainerPlacefulSetup, unittest.TestCase):

    def setUp(self):
        ContainerPlacefulSetup.setUp(self)
        provideAdapter(ObjectMover)
        provideAdapter(ContainerItemRenamer)
        provideAdapter(ObstinateNameChooser)

    def test_obstinatenamechooser(self):
        container = TestContainer()
        container['foobar'] = Contained()
        renamer = IContainerItemRenamer(container)

        renamer.renameItem('foobar', 'newname')
        self.assertEqual(list(container), ['foobar'])


container_setup = PlacelessSetup()


def globalSetUp(test):
    testing.setUp()
    eventtesting.setUp()
    container_setup.setUp()


class TestRename(unittest.TestCase):

    def setUp(self):
        globalSetUp(self)

    def tearDown(self):
        testing.tearDown()

    def test_namechooser_rename_preserve_order(self):
        # Test for OrderedContainerItemRenamer.renameItem

        # This is a regression test for
        # http://www.zope.org/Collectors/Zope3-dev/658

        # Also: https://bugs.launchpad.net/zope.copypastemove/+bug/98385
        provideAdapter(ObjectMover)

        # There's an ordered container

        from zope.container.ordered import OrderedContainer
        container = OrderedContainer()

        class Obj(Contained):
            def __init__(self, title):
                self.title = title

        objects = [Obj('Foo'), Obj('Bar'), Obj('Baz')]
        container['foo'] = objects[0]
        container['bar'] = objects[1]
        container['baz'] = objects[2]

        # with a custom name chooser

        import codecs

        from zope.container.interfaces import INameChooser
        from zope.interface import Interface
        from zope.interface import implementer

        class IMyContainer(Interface):
            "An interface"
        @adapter(IMyContainer)
        @implementer(INameChooser)
        class MyNameChooser:
            def __init__(self, container):
                self.container = container

            def chooseName(self, name, obj):
                return codecs.getencoder('rot-13')(name)[0]
        provideAdapter(MyNameChooser)

        from zope.interface import alsoProvides
        alsoProvides(container, IMyContainer)

        # OrderedContainerItemRenamer renames and preserves the order of items

        from zope.copypastemove import OrderedContainerItemRenamer
        renamer = OrderedContainerItemRenamer(container)
        self.assertEqual(renamer.renameItem('bar', 'quux'),
                         'dhhk')

        self.assertEqual(list(container.keys()),
                         ['foo', 'dhhk', 'baz'])
        self.assertEqual(container.values(),
                         objects)


def test_suite():
    flags = (doctest.NORMALIZE_WHITESPACE
             | doctest.ELLIPSIS
             | doctest.IGNORE_EXCEPTION_DETAIL)
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(
            'zope.copypastemove',
            setUp=globalSetUp, tearDown=testing.tearDown,
            optionflags=flags),
    ))
