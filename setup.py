##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.copypastemove package

$Id$
"""
import os
from setuptools import setup, find_packages

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.copypastemove',
      version = '3.5.0dev',
      url='http://pypi.python.org/pypi/zope.copypastemove',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description="Copy, Paste and Move support for content components.",
      long_description=long_description,
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Framework :: Zope3',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      extras_require=dict(
          test=['zope.app.testing', 'zope.app.principalannotation']),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.exceptions',
                        'zope.component',
                        'zope.event',
                        'zope.location',
                        'zope.annotation',
                        'zope.lifecycleevent',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
