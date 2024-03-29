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
"""Copy, Paste and Move support for content components
"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.container.constraints import checkObject
from zope.container.interfaces import IContainer
from zope.container.interfaces import INameChooser
from zope.container.interfaces import IOrderedContainer
from zope.container.sample import SampleContainer
from zope.copy import copy
from zope.event import notify
from zope.exceptions import DuplicationError
from zope.interface import Invalid
from zope.interface import implementer
from zope.lifecycleevent import ObjectCopiedEvent
from zope.location.interfaces import IContained
from zope.location.interfaces import ISublocations

from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove.interfaces import IObjectMover
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.copypastemove.interfaces import ItemNotFoundError


@adapter(IContained)
@implementer(IObjectMover)
class ObjectMover:
    """Adapter for moving objects between containers

    To use an object mover, pass a contained `object` to the class.
    The contained `object` should implement `IContained`.  It should be
    contained in a container that has an adapter to `INameChooser`.


    >>> from zope.container.contained import Contained
    >>> ob = Contained()
    >>> container = ExampleContainer()
    >>> container['foo'] = ob
    >>> mover = ObjectMover(ob)

    In addition to moving objects, object movers can tell you if the
    object is movable:

    >>> mover.moveable()
    True

    which, at least for now, they always are.  A better question to
    ask is whether we can move to a particular container. Right now,
    we can always move to a container of the same class:

    >>> container2 = ExampleContainer()
    >>> mover.moveableTo(container2)
    True
    >>> mover.moveableTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

    Of course, once we've decided we can move an object, we can use
    the mover to do so:

    >>> mover.moveTo(container2)
    'foo'
    >>> list(container)
    []
    >>> list(container2)
    ['foo']
    >>> ob.__parent__ is container2
    True

    We can also specify a name:

    >>> mover.moveTo(container2, 'bar')
    'bar'
    >>> list(container2)
    ['bar']
    >>> ob.__parent__ is container2
    True
    >>> ob.__name__
    'bar'

    But we may not use the same name given, if the name is already in
    use:

    >>> container2['splat'] = 1
    >>> mover.moveTo(container2, 'splat')
    'splat_'
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    ['splat', 'splat_']
    >>> ob.__name__
    'splat_'


    If we try to move to an invalid container, we'll get an error:

    >>> mover.moveTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.


    Do a test for preconditions:

    >>> import zope.interface
    >>> import zope.schema
    >>> def preNoZ(container, name, ob):
    ...     "Silly precondition example"
    ...     if name.startswith("Z"):
    ...         raise zope.interface.Invalid("Invalid name.")

    >>> class I1(zope.interface.Interface):
    ...     def __setitem__(name, on):
    ...         "Add an item"
    ...     __setitem__.precondition = preNoZ

    >>> from zope.container.interfaces import IContainer
    >>> @zope.interface.implementer(I1, IContainer)
    ... class C1(object):
    ...     def __repr__(self):
    ...         return 'C1'

    >>> container3 = C1()
    >>> mover.moveableTo(container3, 'ZDummy')
    False
    >>> mover.moveableTo(container3, 'newName')
    True

    And a test for constraints:

    >>> def con1(container):
    ...     "silly container constraint"
    ...     if not hasattr(container, 'x'):
    ...         return False
    ...     return True
    ...
    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint=con1)
    ...
    >>> @zope.interface.implementer(I2)
    ... class constrainedObject(object):
    ...     def __init__(self):
    ...         self.__name__ = 'constrainedObject'
    ...
    >>> cO = constrainedObject()
    >>> mover2 = ObjectMover(cO)
    >>> mover2.moveableTo(container)
    False
    >>> container.x = 1
    >>> mover2.moveableTo(container)
    True

    """

    def __init__(self, object):
        self.context = object
        self.__parent__ = object  # TODO: see if we can automate this

    def moveTo(self, target, new_name=None):
        """Move this object to the `target` given.

        Returns the new name within the `target`
        """

        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        checkObject(target, new_name, obj)

        if target is container and new_name == orig_name:
            # Nothing to do
            return

        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        if target is container and new_name == orig_name:
            # obstinate namechooser
            return

        target[new_name] = obj
        del container[orig_name]
        return new_name

    def moveable(self):
        """Returns ``True`` if the object is moveable, otherwise ``False``."""
        return True

    def moveableTo(self, target, name=None):
        """Say whether the object can be moved to the given target.

        Returns ``True`` if it can be moved there. Otherwise, returns
        ``False``.
        """
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self.context)
        except Invalid:
            return False
        return True


@adapter(IContained)
@implementer(IObjectCopier)
class ObjectCopier:
    """Adapter for copying objects between containers

    To use an object copier, pass a contained `object` to the class.
    The contained `object` should implement `IContained`.  It should be
    contained in a container that has an adapter to `INameChooser`.

    >>> from zope.container.contained import Contained
    >>> ob = Contained()
    >>> container = ExampleContainer()
    >>> container['foo'] = ob
    >>> copier = ObjectCopier(ob)

    In addition to moving objects, object copiers can tell you if the
    object is movable:

    >>> copier.copyable()
    True

    which, at least for now, they always are.  A better question to
    ask is whether we can copy to a particular container. Right now,
    we can always copy to a container of the same class:

    >>> container2 = ExampleContainer()
    >>> copier.copyableTo(container2)
    True
    >>> copier.copyableTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

    Of course, once we've decided we can copy an object, we can use
    the copier to do so:

    >>> copier.copyTo(container2)
    'foo'
    >>> list(container)
    ['foo']
    >>> list(container2)
    ['foo']
    >>> ob.__parent__ is container
    True
    >>> container2['foo'] is ob
    False
    >>> container2['foo'].__parent__ is container2
    True
    >>> container2['foo'].__name__
    'foo'

    We can also specify a name:

    >>> copier.copyTo(container2, 'bar')
    'bar'
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    ['bar', 'foo']

    >>> ob.__parent__ is container
    True
    >>> container2['bar'] is ob
    False
    >>> container2['bar'].__parent__ is container2
    True
    >>> container2['bar'].__name__
    'bar'

    But we may not use the same name given, if the name is already in
    use:

    >>> copier.copyTo(container2, 'bar')
    'bar_'
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    ['bar', 'bar_', 'foo']
    >>> container2['bar_'].__name__
    'bar_'


    If we try to copy to an invalid container, we'll get an error:

    >>> copier.copyTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

    Do a test for preconditions:

    >>> import zope.interface
    >>> import zope.schema
    >>> def preNoZ(container, name, ob):
    ...     "Silly precondition example"
    ...     if name.startswith("Z"):
    ...         raise zope.interface.Invalid("Invalid name.")

    >>> class I1(zope.interface.Interface):
    ...     def __setitem__(name, on):
    ...         "Add an item"
    ...     __setitem__.precondition = preNoZ

    >>> from zope.container.interfaces import IContainer
    >>> @zope.interface.implementer(I1, IContainer)
    ... class C1(object):
    ...     def __repr__(self):
    ...         return 'C1'

    >>> container3 = C1()
    >>> copier.copyableTo(container3, 'ZDummy')
    False
    >>> copier.copyableTo(container3, 'newName')
    True

    And a test for constraints:

    >>> def con1(container):
    ...     "silly container constraint"
    ...     if not hasattr(container, 'x'):
    ...         return False
    ...     return True
    ...
    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint=con1)
    ...
    >>> @zope.interface.implementer(I2)
    ... class constrainedObject(object):
    ...     def __init__(self):
    ...         self.__name__ = 'constrainedObject'
    ...
    >>> cO = constrainedObject()
    >>> copier2 = ObjectCopier(cO)
    >>> copier2.copyableTo(container)
    False
    >>> container.x = 1
    >>> copier2.copyableTo(container)
    True

    """

    def __init__(self, object):
        self.context = object
        self.__parent__ = object  # TODO: see if we can automate this

    def copyTo(self, target, new_name=None):
        """Copy this object to the `target` given.

        Returns the new name within the `target`. After the copy
        is created and before adding it to the target container,
        an `IObjectCopied` event is published.
        """
        obj = self.context

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        checkObject(target, new_name, obj)

        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        new = copy(obj)
        notify(ObjectCopiedEvent(new, obj))

        target[new_name] = new
        return new_name

    def copyable(self):
        """Returns True if the object is copyable, otherwise False."""
        return True

    def copyableTo(self, target, name=None):
        """Say whether the object can be copied to the given `target`.

        Returns ``True`` if it can be copied there. Otherwise, returns
        ``False``.
        """
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self.context)
        except Invalid:
            return False
        return True


@adapter(IContainer)
@implementer(IContainerItemRenamer)
class ContainerItemRenamer:
    """An IContainerItemRenamer adapter for containers.

    This adapter uses IObjectMover to move an item within the same container
    to a different name. We need to first setup an adapter for IObjectMover:

      >>> from zope.location.interfaces import IContained
      >>> gsm = zope.component.getGlobalSiteManager()
      >>> gsm.registerAdapter(ObjectMover, (IContained, ), IObjectMover)

    To rename an item in a container, instantiate a ContainerItemRenamer
    with the container:

      >>> container = SampleContainer()
      >>> renamer = ContainerItemRenamer(container)

    For this example, we'll rename an item 'foo':

      >>> from zope.container.contained import Contained
      >>> foo = Contained()
      >>> container['foo'] = foo
      >>> container['foo'] is foo
      True

    to 'bar':

      >>> renamer.renameItem('foo', 'bar')
      'bar'
      >>> container['foo'] is foo
      Traceback (most recent call last):
      KeyError: 'foo'
      >>> container['bar'] is foo
      True

    If the item being renamed isn't in the container, a NotFoundError is
    raised:

      >>> renamer.renameItem('foo', 'bar') # doctest:+ELLIPSIS
      Traceback (most recent call last):
      ItemNotFoundError: (<...SampleContainer...>, 'foo')

    If the new item name already exists, a DuplicationError is raised:

      >>> renamer.renameItem('bar', 'bar')
      Traceback (most recent call last):
      DuplicationError: bar is already in use

    """

    def __init__(self, container):
        self.container = container

    def renameItem(self, oldName, newName):
        return self._renameItem(oldName, newName)

    def _renameItem(self, oldName, newName):
        object = self.container.get(oldName)
        if object is None:
            raise ItemNotFoundError(self.container, oldName)
        mover = IObjectMover(object)

        if newName in self.container:
            raise DuplicationError("%s is already in use" % newName)

        return mover.moveTo(self.container, newName)


@adapter(IOrderedContainer)
@implementer(IContainerItemRenamer)
class OrderedContainerItemRenamer(ContainerItemRenamer):
    """Renames items within an ordered container.

    This renamer preserves the original order of the contained items.

    To illustrate, we need to setup an IObjectMover, which is used in the
    renaming:

      >>> from zope.location.interfaces import IContained
      >>> gsm = zope.component.getGlobalSiteManager()
      >>> gsm.registerAdapter(ObjectMover, (IContained, ), IObjectMover)

    To rename an item in an ordered container, we instantiate a
    OrderedContainerItemRenamer with the container:

      >>> from zope.container.ordered import OrderedContainer
      >>> container = OrderedContainer()
      >>> renamer = OrderedContainerItemRenamer(container)

    We'll add three items to the container:

      >>> container['1'] = 'Item 1'
      >>> container['2'] = 'Item 2'
      >>> container['3'] = 'Item 3'
      >>> container.items()
      [('1', 'Item 1'), ('2', 'Item 2'), ('3', 'Item 3')]

    When we rename one of the items:

      >>> renamer.renameItem('1', 'I')
      'I'

    the order is preserved:

      >>> container.items()
      [('I', 'Item 1'), ('2', 'Item 2'), ('3', 'Item 3')]

    Renaming the other two items also preserves the origina order:

      >>> renamer.renameItem('2', 'II')
      'II'
      >>> renamer.renameItem('3', 'III')
      'III'
      >>> container.items()
      [('I', 'Item 1'), ('II', 'Item 2'), ('III', 'Item 3')]

    As with the standard renamer, trying to rename a non-existent item raises
    an error:

      >>> renamer.renameItem('IV', '4') # doctest:+ELLIPSIS
      Traceback (most recent call last):
      ItemNotFoundError: (<...OrderedContainer...>, 'IV')

    And if the new item name already exists, a DuplicationError is raised:

      >>> renamer.renameItem('III', 'I')
      Traceback (most recent call last):
      DuplicationError: I is already in use

    """

    def renameItem(self, oldName, newName):
        order = list(self.container.keys())
        newName = self._renameItem(oldName, newName)
        order[order.index(oldName)] = newName
        self.container.updateOrder(order)
        return newName


@adapter(IAnnotations)
@implementer(IPrincipalClipboard)
class PrincipalClipboard:
    """Principal clipboard

    Clipboard information consists of mappings of
    ``{'action':action, 'target':target}``.
    """

    def __init__(self, annotation):
        self.context = annotation

    def clearContents(self):
        """Clear the contents of the clipboard"""
        self.context['clipboard'] = ()

    def addItems(self, action, targets):
        """Add new items to the clipboard"""
        contents = self.getContents()
        actions = []
        for target in targets:
            actions.append({'action': action, 'target': target})
        self.context['clipboard'] = contents + tuple(actions)

    def setContents(self, clipboard):
        """Replace the contents of the clipboard by the given value"""
        self.context['clipboard'] = clipboard

    def getContents(self):
        """Return the contents of the clipboard"""
        return self.context.get('clipboard', ())


@implementer(INameChooser)
class ExampleContainer(SampleContainer):
    # Sample container used for examples in doc stringss in this module

    def chooseName(self, name, ob):
        while name in self:
            name += '_'
        return name


def dispatchToSublocations(object, event):
    """Dispatches an event to sublocations of a given object.

    This handler is used to dispatch copy events to sublocations.

    To illustrate, we'll first create a hierarchy of objects:

      >>> class L(object):
      ...     def __init__(self, name):
      ...         self.__name__ = name
      ...         self.__parent__ = None
      ...     def __repr__(self):
      ...         return '%s(%s)' % (self.__class__.__name__, self.__name__)

      >>> @implementer(ISublocations)
      ... class C(L):
      ...     def __init__(self, name, *subs):
      ...         L.__init__(self, name)
      ...         self.subs = subs
      ...         for sub in subs:
      ...             sub.__parent__ = self
      ...     def sublocations(self):
      ...         return self.subs

      >>> c = C(1,
      ...       C(11,
      ...         L(111),
      ...         L(112),
      ...         ),
      ...       C(12,
      ...         L(121),
      ...         L(122),
      ...         L(123),
      ...         L(124),
      ...         ),
      ...       L(13),
      ...       )

    and a handler for copy events that records the objects it's seen:

      >>> seen = []
      >>> def handler(ob, event):
      ...     seen.append((ob, event.object))

    Finally, we need to register our handler for copy events:

      >>> from zope.lifecycleevent.interfaces import IObjectCopiedEvent
      >>> gsm = zope.component.getGlobalSiteManager()
      >>> gsm.registerHandler(handler, [None, IObjectCopiedEvent])

    and this function as a dispatcher:

      >>> gsm.registerHandler(dispatchToSublocations,
      ...                     [None, IObjectCopiedEvent])

    When we notify that our root object has been copied:

      >>> notify(ObjectCopiedEvent(c, L('')))

    we see that our handler has seen all of the subobjects:

      >>> seenreprs = sorted(map(repr, seen))
      >>> seenreprs #doctest: +NORMALIZE_WHITESPACE
      ['(C(1), C(1))', '(C(11), C(1))', '(C(12), C(1))',
       '(L(111), C(1))', '(L(112), C(1))', '(L(121), C(1))',
       '(L(122), C(1))', '(L(123), C(1))', '(L(124), C(1))',
       '(L(13), C(1))']
    """
    subs = ISublocations(object, None)
    if subs is not None:
        for sub in subs.sublocations():
            zope.component.handle(sub, event)
