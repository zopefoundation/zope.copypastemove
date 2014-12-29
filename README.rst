``zope.copypastemove``
======================

.. image:: https://travis-ci.org/zopefoundation/zope.copypastemove.png?branch=master
        :target: https://travis-ci.org/zopefoundation/zope.copypastemove

This package provides Copy, Paste and Move support for content
components in Zope.  In particular, it defines the following
interfaces for this kind of functionality:

* ``IObjectMover``,

* ``IObjectCopier``,

* ``IContentItemRenamer``,

* ``IPrincipalClipboard``

as well as standard implementations for containers and contained
objects as known from the ``zope.container`` package.
