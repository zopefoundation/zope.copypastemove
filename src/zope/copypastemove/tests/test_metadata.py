##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""Object copier metadata tests"""

import datetime
import unittest
import zope.annotation
import zope.annotation.attribute
import zope.component
import zope.container.contained
import zope.container.interfaces
import zope.container.sample
import zope.container.testing
import zope.copypastemove
import zope.dublincore.testing
import zope.dublincore.timeannotators
import zope.lifecycleevent.interfaces
import zope.location.interfaces
import zope.traversing.api


class CopyCreationTimeTest(zope.container.testing.ContainerPlacefulSetup,
                           unittest.TestCase):

    def setUp(self):
        super(CopyCreationTimeTest, self).setUp()
        # We need a folder hierarchy for copying:
        self.buildFolders()
        # We need the default zope.dublincore adapters:
        zope.dublincore.testing.setUpDublinCore()
        # And the created annotator for the ObjectCopiedEvent
        zope.component.provideHandler(
            zope.dublincore.timeannotators.CreatedAnnotator,
            [zope.lifecycleevent.interfaces.IObjectCopiedEvent])
        zope.component.provideHandler(
            zope.dublincore.timeannotators.CreatedAnnotator,
            [None, zope.lifecycleevent.interfaces.IObjectCopiedEvent])
        # The metadata are stored in annotations on the container:
        zope.interface.classImplements(
            zope.container.sample.SampleContainer,
            zope.annotation.IAttributeAnnotatable)
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)
        # We need the dispatch the copied event to the sub locations:
        zope.component.provideHandler(
            zope.copypastemove.dispatchToSublocations,
            [None, zope.lifecycleevent.interfaces.IObjectCopiedEvent])
        zope.component.provideAdapter(
            zope.container.contained.ContainerSublocations,
            [zope.container.interfaces.IReadContainer],
            zope.location.interfaces.ISublocations)

    def test_copy(self):
        from zope.dublincore.interfaces import IZopeDublinCore
        from zope.traversing.api import traverse

        # Neither the original folder nor one of its subfolders have a
        # creation date as there was no event on creation:
        folder = traverse(self.rootFolder, 'folder1')
        self.assertTrue(IZopeDublinCore(folder).created is None)
        subfolder = traverse(self.rootFolder, 'folder1/folder1_1')
        self.assertTrue(IZopeDublinCore(subfolder).created is None)

        # After copying the folder, it has a creation date:
        copier = zope.copypastemove.ObjectCopier(folder)
        copier.copyTo(self.rootFolder, 'folder-copy')
        folder_copy = traverse(self.rootFolder, 'folder-copy')
        self.assertTrue(isinstance(IZopeDublinCore(folder_copy).created,
                                   datetime.datetime))

        # The subfolder has a creation date, too:
        subfolder_copy = traverse(self.rootFolder, 'folder-copy/folder1_1')
        self.assertTrue(isinstance(IZopeDublinCore(subfolder_copy).created,
                                   datetime.datetime))

