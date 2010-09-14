##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################

version = '3.8.0'

from setuptools import setup, find_packages

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.copypastemove',
      version = version,
      url='http://pypi.python.org/pypi/zope.copypastemove',
      license='ZPL 2.1',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
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
          test=['zope.principalannotation',
                'zope.testing',
                'zope.traversing',
                'zope.dublincore >= 3.8',
                ]),
      install_requires=['setuptools',
                        'zope.annotation',
                        'zope.component',
                        'zope.container',
                        'zope.copy',
                        'zope.event',
                        'zope.exceptions',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.location',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
