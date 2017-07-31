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
import re
import unittest

from zope.component import testing, eventtesting, provideAdapter, adapter
from zope.container.testing import PlacelessSetup, ContainerPlacefulSetup
from zope.copypastemove import ContainerItemRenamer, ObjectMover
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.container.contained import Contained, NameChooser
from zope.container.sample import SampleContainer
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
])

class TestContainer(SampleContainer):
    pass

@adapter(TestContainer)
class ObstinateNameChooser(NameChooser):

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
        from zope.interface import implementer, Interface
        from zope.container.interfaces import INameChooser
        class IMyContainer(Interface):
            "An interface"
        @adapter(IMyContainer)
        @implementer(INameChooser)
        class MyNameChooser(object):
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
                         u'dhhk')

        self.assertEqual(list(container.keys()),
                         [u'foo', u'dhhk', u'baz'])
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
            checker=checker, optionflags=flags),
    ))
