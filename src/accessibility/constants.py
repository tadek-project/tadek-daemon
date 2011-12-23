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

__all__ = ["ActionSet", "ButtonSet", "KeySet", "RelationSet",
           "RoleSet", "StateSet", "keyset"]

from tadek.core.constants import *


class ConstantSet(object):
    '''
    Defines a read-only set of related constans, which can be initialized only
    once - by current implementation of the accessibility interface.
    '''
    __slots__ = ("_name", "_items")

    def __init__(self, name, *items):
        self._name = name
        self._items = {}
        # Intializes items of the constant set with None
        for i in items:
            self._items[i] = None

    def __getattr__(self, name):
        '''
        Gets a item value of the constant set given by the name.
        '''
        if name in self.__slots__:
            return object.__getattribute__(self, name)
        elif name in self._items and self._items[name] is not None:
            return self._items[name]
        else:
            raise AttributeError("'%s' set has no item '%s'"
                                  % (self._name, name))

    def __setattr__(self, name, value):
        '''
        Sets new item value of the constant set given by the name.
        '''
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        elif name not in self._items:
            raise AttributeError("'%s' set has no item '%s'"
                                  % (self._name, name))
        elif self._items[name] is not None:
            raise ValueError("'%s' item of '%s' set already initialized"
                              % (name, self._name))
        else:
            self._items[name] = value

    def __iter__(self):
        '''
        Iterator that yields one item name of the constant set per iteration.
        '''
        for i in self._items:
            if self._items[i] is not None:
                yield self._items[i]

    def name(self, value):
        '''
        Returns a item name of the constant set given by its value.
        '''
        if value is not None:
            for n, v in self._items.iteritems():
                if v == value:
                    return n
        return None


class ActionSet(ConstantSet):
    '''
    An action set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "Action", *ACTIONS)


class RelationSet(ConstantSet):
    '''
    A relation set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "Relation", *RELATIONS)


class RoleSet(ConstantSet):
    '''
    A role set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "Role", *ROLES)


class StateSet(ConstantSet):
    '''
    A state set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "State", *STATES)


class ButtonSet(ConstantSet):
    '''
    A button set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "Button", *BUTTONS)


class KeySet(ConstantSet):
    '''
    A key set.
    '''
    def __init__(self):
        ConstantSet.__init__(self, "Key", *KEY_SYMS.keys())

keyset = KeySet()
# Set default values:
for key, code in KEY_SYMS.iteritems():
    setattr(keyset, key, code)

