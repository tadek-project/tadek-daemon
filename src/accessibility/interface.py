################################################################################
##                                                                            ##
## This file is a part of TADEK.                                              ##
##                                                                            ##
## TADEK - Test Automation in a Distributed Environment                       ##
## (http://tadek.comarch.com)                                                 ##
##                                                                            ##
## Copyright (C) 2011 Comarch S.A.                                            ##
## All rights reserved.                                                       ##
##                                                                            ##
## TADEK is free software for non-commercial purposes. For commercial ones    ##
## we offer a commercial license. Please check http://tadek.comarch.com for   ##
## details or write to tadek-licenses@comarch.com                             ##
##                                                                            ##
## You can redistribute it and/or modify it under the terms of the            ##
## GNU General Public License as published by the Free Software Foundation,   ##
## either version 3 of the License, or (at your option) any later version.    ##
##                                                                            ##
## TADEK is distributed in the hope that it will be useful,                   ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
## GNU General Public License for more details.                               ##
##                                                                            ##
## You should have received a copy of the GNU General Public License          ##
## along with TADEK bundled with this file in the file LICENSE.               ##
## If not, see http://www.gnu.org/licenses/.                                  ##
##                                                                            ##
## Please notice that Contributor Agreement applies to any contribution       ##
## you make to TADEK. The Agreement must be completed, signed and sent        ##
## to Comarch before any contribution is made. You should have received       ##
## a copy of Contribution Agreement along with TADEK bundled with this file   ##
## in the file CONTRIBUTION_AGREEMENT.pdf or see http://tadek.comarch.com     ##
## or write to tadek-licenses@comarch.com                                     ##
##                                                                            ##
################################################################################

__all__ = ["decodeResult", "encodeLastArg",
           "IAccessibility", "AccessibilityError"]

import inspect

from tadek.core.utils import encode, decode
from constants import *

def decodeResult(encoding=None):
    '''
    A decorator that decodes result of a decorated function.
    '''
    def decorate(func):
        def getDecoded(*args):
            result = func(*args)
            if result is not None:
                result = decode(result, encoding)
            return result
        return getDecoded
    return decorate

def encodeLastArg(encoding=None):
    '''
    A decorator that encodes the last argument of a decorated function.
    '''
    def decorate(func):
        def getEncoded(*args):
            arg = args[-1]
            args = list(args[:-1])
            if arg is not None:
                arg = encode(arg, encoding)
            args.append(arg)
            return func(*args)
        return getEncoded
    return decorate


class AccessibilityError(Exception):
    '''
    An accessibility exception.
    '''
    pass


class MAccessibility(type):
    '''
    An accessibility metaclass.
    '''
    def __init__(cls, name, bases, attrs):
        if attrs["name"] is None:
            # It's the accessibility interface
            return
        for name, attr in attrs.iteritems():
            if not inspect.isfunction(attr):
                continue
            if attr.__doc__ is None:
                for baseclass in bases:
                    if hasattr(baseclass, name):
                        attr.__doc__ = getattr(baseclass, name).__doc__
                        break


class IAccessibility:
    '''
    An accessibility interface class.
    '''
    __metaclass__ = MAccessibility

    #: A name of an accessibility implementation
    name = None
    actionset = None
    buttonset = None
    keyset = None
    relationset = None
    roleset = None
    stateset = None

# Device:
    def mouseClick(self, x, y, button):
        '''
        Generates a mouse click event at the given absolute x and y coordinate
        using the specified mouse button.

        :param x: Absolute horizontal coordinate
        :type x: integer
        :param y: Absolute vertical coordinate
        :type y: integer
        :param button: Mouse button to click
        :type button: Button
        '''
        raise NotImplementedError

    def mouseDoubleClick(self, x, y, button):
        '''
        Generates a mouse double-click event at the given absolute x and y
        coordinate using the specified mouse button.

        :param x: Absolute horizontal coordinate
        :type x: integer
        :param y: Absolute vertical coordinate
        :type y: integer
        :param button: Mouse button to double-click
        :type button: Button
        '''
        raise NotImplementedError

    def mousePress(self, x, y, button):
        '''
        Generates a mouse press event at the given absolute x and y coordinate
        using the specified mouse button.

        :param x: Absolute horizontal coordinate
        :type x: integer
        :param y: Absolute vertical coordinate
        :type y: integer
        :param button: Mouse button to press
        :type button: Button
        '''
        raise NotImplementedError

    def mouseRelease(self, x, y, button):
        '''
        Generates a mouse release event at the given absolute x and y coordinate
        using the specified mouse button.

        :param x: Absolute horizontal coordinate
        :type x: integer
        :param y: Absolute vertical coordinate
        :type y: integer
        :param button: Mouse button to release
        :type button: Button
        '''
        raise NotImplementedError

    def mouseAbsoluteMotion(self, x, y):
        '''
        Generates a mouse absolute motion event to the given absolute x and y
        coordinate using the specified mouse button.

        :param x: Absolute horizontal coordinate
        :type x: integer
        :param y: Absolute vertical coordinate
        :type y: integer
        '''
        raise NotImplementedError

    def mouseRelativeMotion(self, x, y):
        '''
        Generates a mouse relative motion event to the given relative x and y
        coordinate using the specified mouse button.

        :param x: Relative horizontal coordinate
        :type x: integer
        :param y: Relative vertical coordinate
        :type y: integer
        '''
        raise NotImplementedError

    def keyboardEvent(self, key, modifiers=()):
        '''
        Generates keyboard event of the given key.

        :param key: Hardware kaycode or symbolic key string
        :type key: integer or string
        :param modifiers:  Codes of key modifiers
        :type modifiers: list
        '''
        if isinstance(key, basestring):
            if hasattr(self.keyset, key):
                key = getattr(self.keyset, key)
            else:
                key = ord(key)
        elif not isinstance(key, int):
            raise TypeError("Invalid key type: %s" % type(key).__name__)
        for modifier in modifiers:
            if not isinstance(modifier, int):
                raise TypeError("Invalid modifier key type: %s"
                                 % type(modifier).__name__)
        self._keyboardEvent(key, modifiers)

    def _keyboardEvent(self, keycode, modifiers):
        '''
        Generates keyboard event of the given keycode or symbolic key string.

        :param keycode: A hardware key code
        :type keycode: integer
        :param modifiers:  Codes of key modifiers
        :type modifiers: list
        '''
        raise NotImplementedError

# Object children:
    def getDesktop(self):
        '''
        Gets an accessible object of the desktop.

        :return: Desktop accessible object
        :rtype: Accessible
        '''
        raise NotImplementedError

    def children(self, parent=None):
        '''
        Iterator that yields one child of the given accessible parent object per
        iteration. If parent is not given then registered applications are
        yielded.

        :param parent: Parent accessible object or None
        :type parent: Accessible
        :return: Child accessible object, if any
        :rtype: Accessible
        '''
        raise NotImplementedError

    def countChildren(self, parent=None):
        '''
        Returns number of children of the given accessible parent object.
        If parent is not given then number of  registered applications is
        returned.

        :param parent: Parent accessible object or None
        :type parent: Accessible
        :return: Number of children
        :rtype: integer
        '''
        raise NotImplementedError

    def getChild(self, parent=None, index=0):
        '''
        Gets a child of the specified index from the given accessible parent
        object. If parent is not given then registered application of the index
        is returned.

        :param index: Index of desired child
        :type index: integer
        :param parent: Parent accessible object or None
        :type parent: Accessible
        :return: Child accessible object
        :rtype: Accessible
        '''
        n = self.countChildren(parent)
        if index >= n or index < -n:
            return None
        elif index < 0:
            index += n
        return self._getChild(parent, index)

    def _getChild(self, parent, index):
        '''
        Implementation of getChild method.
        '''
        raise NotImplementedError

    def getParent(self, accessible):
        '''
        Gets a parent of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Parent of the accessible object
        :rtype: Accessible
        '''
        raise NotImplementedError

# Object properties:
    def getIndex(self, accessible):
        '''
        Gets an index in parent of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Index of the accessible object
        :rtype: integer
        '''
        raise NotImplementedError

    def getName(self, accessible):
        '''
        Gets a name of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Name of the accessible object
        :rtype: string
        '''
        raise NotImplementedError

    def getDescription(self, accessible):
        '''
        Gets a description of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Description of the accessible object
        :rtype: string
        '''
        raise NotImplementedError

    def getRole(self, accessible):
        '''
        Gets a role of the given accessible object. Type of a returned role
        depends on an implementation of this method.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Role of the accessible object
        :rtype: Role
        '''
        raise NotImplementedError

    def getRoleName(self, accessible):
        '''
        Gets a role name of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Role name of the accessible object
        :rtype: string
        '''
        rolename = self.roleset.name(self.getRole(accessible))
        if not rolename:
            rolename = "UNKNOWN"
        return rolename

    def getPosition(self, accessible):
        '''
        Gets a position in pixels of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Position of the accessible object as (x, y)
        :rtype: tuple
        '''
        raise NotImplementedError

    def getSize(self, accessible):
        '''
        Gets a size in pixels of the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Size of the accessible object as (width, height)
        :rtype: tuple
        '''
        raise NotImplementedError

    def getAttributes(self, accessible):
        '''
        Gets a dictionary containing names and values of attributes  of
        the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Attributes of the accessible object as {name: value}
        :rtype: dictionary
        '''
        raise NotImplementedError

    def getText(self, accessible):
        '''
        Gets text from the given accessible object if any.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Text from the accessible object
        :rtype: string
        '''
        raise NotImplementedError

    def setText(self, accessible, text):
        '''
        Sets text of the given accessible object if possible.

        :param accessible: Accessible object
        :type accessible: Accessible
        :param text: New text of the accessible object
        :type text: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        raise NotImplementedError

    def getValue(self, accessible):
        '''
        Gets a value from the given accessible object if any.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Value from the accessible object
        :rtype: float
        '''
        raise NotImplementedError

    def setValue(self, accessible, value):
        '''
        Sets a value of the given accessible object if possible.

        :param accessible: Accessible object
        :type accessible: Accessible
        :param value: New value of the accessible object
        :type value: float
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        raise NotImplementedError

    def getImage(self, accessible):
        '''
        Gets image of the given accessible object or None.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Image of the accessible object or None
        :rtype: Image
        '''
        raise NotImplementedError

    def grabFocus(self, accessible):
        '''
        Sets input focus to the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        raise NotImplementedError

# Object actions:
    def actions(self, accessible):
        '''
        Iterator that yields one action of the given accessible object per
        iteration. Type of returned action depends on an implementation of this
        method.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Action of the accessible object
        :rtype: Action
        '''
        raise NotImplementedError

    def actionNames(self, accessible):
        '''
        Iterator that yields one action name of the given accessible object per
        iteration.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Name of an action
        :rtype: string
        '''
        for action in self.actions(accessible):
            name = self.actionset.name(action)
            if name is not None:
                yield name

    def doAction(self, accessible, action):
        '''
        Performs the specified action on the given accessible object.

        :param accessible: Accessible object
        :type accessible: Accessible
        :param action: Action to invoke
        :type action: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        raise NotImplementedError

# Object relations:
    def relations(self, accessible):
        '''
        Iterator that yields one relation of the given accessible object per
        iteration. Type of returned relation depends on an implementation of
        this method.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Relation of the accessible object
        :rtype: Relation
        '''
        raise NotImplementedError

    def relationNames(self, accessible):
        '''
        Iterator that yields one relation name of the given accessible object
        per iteration.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return: Name of an relation
        :rtype: string
        '''
        for relation in self.relations(accessible):
            name = self.relationset.name(relation)
            if name is not None:
                yield name

    def relationTargets(self, accessible, relation):
        '''
        Iterator that yields one target accessible object of the specified
        relation of the given accessible object per iteration.

        :param accessible: Accessible object
        :type accessible: Accessible
        :param relation: Relation of the accessible object
        :type relation: Relation
        :return: Target accessible object
        :rtype: Accessible
        '''
        raise NotImplementedError

# Object states:
    def states(self, accessible):
        '''
        Iterator that yields one state of the given accessible object per
        iteration.

        :param accessible: Accessible object
        :type accessible: Accessible
        :return relation: State of the accessible object
        :rtype relation: State
        '''
        raise NotImplementedError

    def inState(self, accessible, state):
        '''
        Checks if the given accessible object is in the specified state.

        :param accessible: Accessible object
        :type accessible: Accessible
        :param relation: State of the accessible object
        :type relation: State
        :return: True if the accessible object is in the state, False otherwise
        :rtype: boolesn
        '''
        raise NotImplementedError

