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

import accessibility

# Number of all available accessibilities
a11yCount = len(accessibility.all())

def accessible(path):
    '''
    Gets an accessible object of the given path.

    :param path: A path of an accessible object
    :type path: tadek.core.accessible.Path
    :return: An accessible object or None if it does not exist
    :rtype: accessible or NoneType
    '''
    if not path.tuple:
        return None, None
    try:
        a11y = accessibility.all()[path.tuple[0]]
    except IndexError:
        return None, None
    obj = None
    try:
        for index in path.tuple[1:]:
            obj = a11y.getChild(obj, index)
            if obj is None:
                return None, None
    except IndexError:
        return None, None
    return a11y, obj


class Provider(object):
    '''
    A base class of iterators those iterate through children/descendants of
    given accessible objects.
    '''
    def __init__(self, a11y, obj, path):
        self._a11y = a11y
        self._obj = obj
        self._path = path

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration


class Children(Provider):
    '''
    A class of iterators those iterate only through direct children of a given
    accessible.
    '''
    def __init__(self, a11y, obj, path):
        Provider.__init__(self, a11y, obj, path)
        self._index = 0
        if self._a11y is None:
            self._children = iter(accessibility.all())
        else:
            self._children = self._a11y.children(obj)

    def next(self):
        path = self._path.child(self._index)
        self._index += 1
        if self._a11y is None:
            a11y = self._children.next()
            obj = None
        else:
            a11y = self._a11y
            obj = self._children.next()
        return a11y, obj, path


class ChildrenBackwards(Provider):
    '''
    A class of backward iterators those iterate only through direct children of
    a given accessible starting from the very last one.
    '''
    def __init__(self, a11y, obj, path):
        Provider.__init__(self, a11y, obj, path)
        if self._a11y is None:
            self._index = a11yCount
        else:
            self._index = self._a11y.countChildren(obj)

    def next(self):
        self._index -= 1
        if self._index < 0:
            raise StopIteration
        path = self._path.child(self._index)
        try:
            if self._a11y is None:
                a11y = accessibility.all()[self._index]
                obj = None
            else:
                a11y = self._a11y
                obj = self._a11y.getChild(self._obj, self._index)
        except IndexError:
            raise StopIteration
        return a11y, obj, path


class Descendants(Provider):
    '''
    A class of iterators those iterate level by level through descendants of
    a given accessible.
    '''
    def __init__(self, a11y, obj, path):
        Provider.__init__(self, a11y, obj, path)
        self._index = 0
        if self._a11y is None:
            self._count = a11yCount
        else:
            self._count = self._a11y.countChildren(self._obj)
        self._queue = []

    def next(self):
        if self._a11y is None and self._index < self._count:
            a11y = accessibility.all()[self._index]
            obj = None
            count = a11y.countChildren()
        else:
            if self._index >= self._count:
                if not self._queue:
                    raise StopIteration
                self._a11y, self._obj, self._path = self._queue.pop(0)
                self._index = 0
                self._count = self._a11y.countChildren(self._obj)
            a11y = self._a11y
            obj = self._a11y.getChild(self._obj, self._index)
            count = self._a11y.countChildren(obj)
        path = self._path.child(self._index)
        if count:
            self._queue.append((a11y, obj, path))
        self._index += 1
        return a11y, obj, path

