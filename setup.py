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
from setuptools import setup, find_packages

def alltests():
    import os
    import sys
    import unittest
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    return unittest.TestSuite(suites)

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.copypastemove',
      version='4.0.0a1',
      url='http://pypi.python.org/pypi/zope.copypastemove',
      license='ZPL 2.1',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description="Copy, Paste and Move support for content components.",
      long_description=long_description,
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
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
                ],
          zcml=[
            'zope.component[zcml]',
            'zope.configuration',
            'zope.security[zcml]',
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
      tests_require = [
          'zope.dublincore',
          'zope.principalannotation',
          'zope.testing',
          'zope.testrunner',
          'zope.traversing',
          ],
      test_suite = '__main__.alltests',
      include_package_data = True,
      zip_safe = False,
      )
