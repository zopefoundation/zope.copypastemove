##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

from zope.testing.doctestunit import DocTestSuite
from zope.component.testing import setUp as setUpCA, tearDown as tearDownCA
from zope.app.container.tests.placelesssetup import PlacelessSetup

container_setup = PlacelessSetup()

def setUp(test):
    setUpCA()
    container_setup.setUp()

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.copypastemove',
                     setUp=setUp, tearDown=tearDownCA),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
