=========
 Changes
=========

6.0 (2025-09-12)
================

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


5.1 (2025-08-27)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


5.0 (2023-07-06)
================

- Add support for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.

- Drop deprecated support for ``python setup.py test``.


4.2.1 (2022-08-25)
==================

- Fix DeprecationWarnings.


4.2.0 (2022-01-24)
==================

- Add support for Python 3.7, 3.8, 3.9, and 3.10.

- Drop support for Python 3.4.


4.1.0 (2017-08-04)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6 and 3.3.


4.0.0 (2014-12-24)
==================

- Add support for PyPy.

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.0a1 (2013-02-24)
====================

- Add support for Python 3.3.

- Replace deprecated ``zope.component.adapts`` usage with equivalent
  ``zope.component.adapter`` decorator.

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.

- Include zcml dependencies in ``configure.zcml``, require the necessary
  packages via a zcml extra, and add tests for zcml.


3.8.0 (2010-09-14)
==================

- Add a test that makes sure that dublin core meta data of folder contents
  get updated when the folder gets copied. (Requires `zope.dublincore` 3.8
  or above.)


3.7.0 (2010-09-14)
==================

- Honor the name given by the ``IObjectMover`` in
  ``OrderedContainerItemRenamer.renameItem``. It now returns the new of the
  obejct, too. Thanks to Marius Gedminas for the patch, and to Justin Ryan
  for the test.  Fixes
  https://bugs.launchpad.net/zope.copypastemove/+bug/98385.

- Add a check for name and container if the namechooser computes a
  name which is the same as the current name.
  Fixes https://bugs.launchpad.net/zope.copypastemove/+bug/123532

- Remove use of ``zope.testing.doctestunit`` in favor of stdlib's ``doctest``.

- Move ``zope.copypastemove``-related tests from ``zope.container`` here.

3.6.0 (2009-12-16)
==================

- Favor ``zope.principalannotation`` over its ``zope.app`` variant.

- Avoid ``zope.app.component`` and testing dependencies.

3.5.2 (2009-08-15)
==================

- Fix documentation for the ``IObjectCopier.copyTo`` method.

- Add a missing dependency on ``zope.app.component``.

3.5.1 (2009-02-09)
==================

- Use the new ``zope.copy`` package for ObjectCopier to provide pluggable
  copying mechanism that is not dependent on ``zope.location`` hardly.

- Move the ``ItemNotFoundError`` exception to the interfaces module as
  it's part of public API.  Old import still works as we actually
  use it where it was previously defined, however, the new import
  place is preferred.

3.5.0 (2009-01-31)
==================

- Use ``zope.container`` instead of ``zope.app.container``.

3.4.1 (2009-01-26)
==================

- Move the test dependencies to a ``test`` extra requirement.

3.4.0 (2007-09-28)
==================

- No further changes since 3.4.0a1.

3.4.0a1 (2007-04-22)
====================

- Initial release as a separate project, corresponds to
  ``zope.copypastemove`` from Zope 3.4.0a1
