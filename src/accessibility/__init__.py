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

import os
import sys

from interface import IAccessibility, AccessibilityError
from constants import ConstantSet

# Reserved module names
_DEFAULT_MODULES = (
    "__init__",
    "interface",
    "constants"
)

def all():
    '''
    Returns a list of all available accessibilities sorted by name.

    :return: A list of accessibilities
    :rtype: tuple
    '''
    if _cache is None:
        _load()
    return _cache

# An accessibility implementations cache
_cache = None

def _load():
    '''
    Loads all available accessibility implementations.
    '''
    global _cache
    mdls = []
    a11ies = {}
    for file in os.listdir(os.path.dirname(__file__)):
        name = os.path.splitext(file)[0]
        if name not in mdls and name not in _DEFAULT_MODULES:
            mdls.append(name)
            name = '.'.join([__name__, name])
            try:
                __import__(name)
            except:
                pass
            else:
                a11y = None
                module = sys.modules[name]
                for attr in vars(module).itervalues():
                    if (isinstance(attr, type) and
                        issubclass(attr, IAccessibility) and
                        getattr(attr, "name", None)):
                        a11y = attr()
                        break
                if a11y and a11y.name not in a11ies:
                    a11ies[a11y.name] = a11y
    _cache = tuple([a11ies[name] for name in sorted(a11ies)])

