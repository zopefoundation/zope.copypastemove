========================
 ``zope.copypastemove``
========================

.. image:: https://img.shields.io/pypi/v/zope.copypastemove.svg
        :target: https://pypi.python.org/pypi/zope.copypastemove/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.copypastemove.svg
        :target: https://pypi.org/project/zope.copypastemove/
        :alt: Supported Python versions

.. image:: https://travis-ci.org/zopefoundation/zope.copypastemove.png?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.copypastemove

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.copypastemove/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.copypastemove?branch=master

This package provides Copy, Paste and Move support for content
components in Zope.  In particular, it defines the following
interfaces for this kind of functionality:

* ``IObjectMover``,

* ``IObjectCopier``,

* ``IContentItemRenamer``,

* ``IPrincipalClipboard``

as well as standard implementations for containers and contained
objects as known from the ``zope.container`` package.
