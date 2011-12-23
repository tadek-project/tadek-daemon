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
import re
import subprocess

from tadek.core import log
from tadek.connection import protocol
from tadek.core.accessible import Path, Accessible, Relation

import providers

# An action name used to grab focus on accessibles
A11Y_ACTION_FOCUS = u"FOCUS"

class Processor(object):
    '''
    A class of simple request processors.
    '''
    def __init__(self):
        self.cache = None

    def __call__(self, request):
        '''
        Processes the given request.
        '''
        log.debug(locals())
        extras = {
            "status": False
        }
        if request.target == protocol.MSG_TARGET_ACCESSIBILITY:
            if request.name == protocol.MSG_NAME_GET:
                params = {}
                for param in request.include:
                    params[str(param)] = True
                status, accessible = accessibilityGet(self, request.path,
                                                      request.depth,
                                                      **params)
                extras = {
                    "status": status,
                    "accessible": accessible
                }
            elif request.name == protocol.MSG_NAME_SEARCH:
                status, accessible = accessibilitySearch(self, request.path,
                                                         request.method,
                                                         **request.predicates)
                extras = {
                    "status": status,
                    "accessible": accessible
                }
            elif request.name == protocol.MSG_NAME_PUT:
                if hasattr(request, 'text'):
                    status = accessibilityPutText(self, request.path,
                                                  request.text)
                elif hasattr(request, 'value'):
                    status = accessibilityPutValue(self, request.path,
                                                   request.value)
                else:
                    raise protocol.UnsupportedMessageError(request.type,
                                                        request.target,
                                                        request.name,
                                                        *request.getParams())
                extras = {
                    "status": status
                }
            elif request.name == protocol.MSG_NAME_EXEC:
                if hasattr(request, 'action'):
                    status = accessibilityExecAction(self, request.path,
                                                     request.action)
                elif (hasattr(request, 'keycode') and
                      hasattr(request, 'modifiers')):
                    status = accessibilityExecKeyboard(self, request.path,
                                                       request.keycode,
                                                       request.modifiers)
                elif (hasattr(request, 'event') and
                      hasattr(request, 'button') and
                      hasattr(request, 'coordinates')):
                    status = accessibilityExecMouse(self, request.path,
                                                    request.event,
                                                    request.button,
                                                    request.coordinates)
                else:
                    raise protocol.UnsupportedMessageError(request.type,
                                                        request.target,
                                                        request.name,
                                                        *request.getParams())
                extras = {
                    "status": status
                }
            else:
                raise protocol.UnsupportedMessageError(request.type,
                                                       request.target,
                                                       request.name,
                                                       *request.getParams())
        elif request.target == protocol.MSG_TARGET_SYSTEM:
            if request.name == protocol.MSG_NAME_GET:
                status, data = systemGet(self, request.path)
                extras = {
                    "status": status,
                    "data": data
                }
            elif request.name == protocol.MSG_NAME_PUT:
                status = systemPut(self, request.path, request.data)
                extras = {
                    "status": status
                }
            elif request.name == protocol.MSG_NAME_EXEC:
                status, stdout, stderr = systemExec(self, request.command,
                                                    request.wait)
                extras = {
                    "status": status,
                    "stdout": stdout,
                    "stderr": stderr
                }
            else:
                raise protocol.UnsupportedMessageError(request.type,
                                                       request.target,
                                                       request.name,
                                                       *request.getParams())
        elif request.target == protocol.MSG_TARGET_EXTENSION:
            params = {}
            for name in request.getParams():
                params[name] = getattr(request, name)
            try:
                ext = protocol.getExtension(request.name)
            except:
                protocol.UnsupportedMessageError(request.type,
                                                 request.target,
                                                 request.name,
                                                 *request.getParams())
            status, extras = ext.response(**params)
            extras["status"] = status
        else:
            raise protocol.UnsupportedMessageError(request.type,
                                                   request.target,
                                                   request.name,
                                                   *request.getParams())
        return protocol.create(protocol.MSG_TYPE_RESPONSE, request.target,
                               request.name, **extras)

# ACCESSIBILITY

def dumpAccessible(a11y, obj, path, depth, name, description, role, count,
                                           position, size, text, value, actions,
                                           states, attributes, relations):
    '''
    Dumps the given accessible object and returns it as an Accessible instance.

    :param a11y: An accessibility releated to a given accessible object
    :type a11y: ModuleType
    :param obj: An accessible object to dump
    :type obj: accessible
    :param path: A path of a given accessible object
    :type path: tadek.core.accessible.Path
    :param depth: A depth of the dump
    :type depth: integer
    :param name: True if the dump should include accessible name
    :type name: boolean
    :param description: True if the dump should include accessible description
    :type description: boolean
    :param role: True if the dump should include accessible role
    :type role: boolean
    :param count: True if the dump should include number of accessible children
    :type count: boolean
    :param position: True if the dump should include accessible position
    :type position: boolean
    :param size: True if the dump should include accessible size
    :type size: boolean
    :param text: True if the dump should include accessible text
    :type text: boolean
    :param value: True if the dump should include accessible value
    :type value: boolean
    :param actions: True if the dump should include accessible actions
    :type actions: boolean
    :param states: True if the dump should include accessible states
    :type states: boolean
    :param attributes: True if the dump should include accessible attributes
    :type attributes: boolean
    :param relations: True if the dump should include accessible relations
    :type relations: bool
    :return: A dumped accessible object
    :rtype: tadek.core.accessible.Accessible
    '''
    log.debug(str(locals()))
    def getPath(a11y, obj, path):
        '''
        Gets a path of the given accessible object.
        '''
        # Insert indexes of accessibility and application of the object
        path = [path.tuple[0], path.tuple[1]]
        while obj is not None:
            path.insert(2, a11y.getIndex(obj))
            obj = a11y.getParent(obj)
        return path
    if obj is None and len(path.tuple) > 1:
        # Invalid accessible object
        return Accessible(path)
    try:
        children = []
        if depth != 0:
            for a, o, p in providers.Children(a11y, obj, path):
                children.append(dumpAccessible(a, o, p, depth-1, name,
                                description, role, count, position, size, text,
                                value, actions, states, attributes, relations))
        acc = Accessible(path, children)
        if a11y is None:
            if count:
                acc.count = providers.a11yCount
        elif obj is None:
            # Accessibility might have only name and numer of children
            if name:
                acc.name = a11y.name
            if count:
                acc.count = a11y.countChildren()
        else:
            if name:
                acc.name = a11y.getName(obj)
            if description:
                acc.description = a11y.getDescription(obj)
            if role:
                acc.role = a11y.getRoleName(obj)
            if count:
                acc.count = a11y.countChildren(obj)
            if position:
                acc.position = a11y.getPosition(obj)
            if size:
                acc.size = a11y.getSize(obj)
            if text:
                acc.text = a11y.getText(obj)
                acc.editable = a11y.inState(obj, a11y.stateset.EDITABLE)
            if value:
                acc.value = a11y.getValue(obj)
            if actions:
                acc.actions = [a for a in a11y.actionNames(obj)]
                if a11y.inState(obj, a11y.stateset.FOCUSABLE):
                    acc.actions.insert(0, A11Y_ACTION_FOCUS)
            if states:
                acc.states = [a11y.stateset.name(s)
                              for s in a11y.states(obj)
                              if a11y.stateset.name(s) is not None]
            if attributes:
                acc.attributes = a11y.getAttributes(obj)
            if relations:
                for relation in a11y.relations(obj):
                    name = a11y.relationset.name(relation)
                    if name:
                        targets = [Path(*getPath(a11y, t, path))
                                   for t in a11y.relationTargets(obj, relation)]
                        acc.relations.append(Relation(name, targets))
    except:
        log.exception("Dumping accessible object error: %s" % path)
        acc = Accessible(path)
    return acc


def accessibilityGet(processor, path, depth, name=False, description=False,
                     role=False, count=False, position=False, size=False,
                     text=False,  value=False, actions=False, states=False,
                     attributes=False, relations=False):
    '''
    Gets an accessible of the given path and depth including specified
    accessible parameters.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of a demanded accessible
    :type path: tadek.core.accessible.Path
    :param depth: A depth of a demanded accessible tree
    :type depth: integer
    :param name: True if a demanded accessible should include name
    :type name: boolean
    :param description: True if a demanded accessible should include description
    :type description: boolean
    :param role: True if a demanded accessible should include role
    :type role: boolean
    :param count: True if a demanded accessible should include child count
    :type count: boolean
    :param position: True if a demanded accessible should include position
    :type position: boolean
    :param size: True if a demanded accessible should include size
    :type size: boolean
    :param text: True if a demanded accessible should include text
    :type text: boolean
    :param value: True if a demanded accessible should include value
    :type value: boolean
    :param actions: True if a demanded accessible should include actions
    :type actions: boolean
    :param states: True if a demanded accessible should include states
    :type states: boolean
    :param attributes: True if a demanded accessible should include attributes
    :type attributes: boolean
    :param relations: True if a demanded accessible should include relations
    :type relations: bool
    :return: A getting accessible status and an accessible of the given path
    :rtype: tuple
    '''
    log.debug(str(locals()))
    # Reset the processor cache
    processor.cache = None
    try:
        a11y, obj = providers.accessible(path)
        if a11y is None and path.tuple:
            log.info("Get accessible of requested path failure: %s" % path)
            return False, Accessible(path)
        processor.cache = (a11y, obj, path)
        return True, dumpAccessible(a11y, obj, path, depth=depth, name=name,
                                description=description, role=role, count=count,
                                position=position, size=size, text=text,
                                value=value, actions=actions, states=states,
                                attributes=attributes, relations=relations)
    except:
        log.exception("Get accessible of requested path error: %s" % path)
        return False, Accessible(path)


def accessibilitySearch(processor, path, method, name=None, description=None,
                        role=None, index=None, count=None, action=None,
                        relation=None, state=None, text=None, nth=0):
    '''
    Searches an accessible using the given method according to specified
    accessible parameters.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of a demanded accessible
    :type path: tadek.core.accessible.Path
    :param method: A search method of accessible
    :type method: string
    :param name: A name of searched accessible or None
    :type name: string or NoneType
    :param description: A description of searched accessible or None
    :type description: string or NoneType
    :param role: A role of searched accessible or None
    :type role: string or NoneType
    :param index: An index of searched accessible or None
    :type index: integer or NoneType
    :param count: A child count of searched accessible or None
    :type count: string or NoneType
    :param action: An action of searched accessible or None
    :type action: string or NoneType
    :param relation: A relation of searched accessible or None
    :type relation: string or NoneType
    :param state: A state of searched accessible or None
    :type state: string or NoneType
    :param text: Text of searched accessible or None
    :type text: string or NoneType
    :param nth: A nth matched accessible
    :type nth: integer
    :return: A searching accessible status and an accessible of the given path
    :rtype: tuple
    '''
    log.debug(str(locals()))
    def matchString(pattern, string):
        '''
        Checks if the give string matches the regular expression pattern.
        '''
        if string is None:
            return False
        match = pattern.match(string)
        return match is not None and match.span() == (0, len(string))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if a11y is None and path.tuple:
            log.info("Accessible of requested path not found: %s" % path)
            return False, Accessible(path)
        if method == protocol.MHD_SEARCH_SIMPLE:
            provider = providers.Children
        elif method == protocol.MHD_SEARCH_BACKWARDS:
            provider = providers.ChildrenBackwards
        elif method == protocol.MHD_SEARCH_DEEP:
            provider = providers.Descendants
        else:
            log.error("Unknown search method: %s" % method)
            return False, Accessible(Path())
        if name and name[0] == '&':
            name = re.compile(name[1:], re.DOTALL)
            cmpName = matchString
        else:
            cmpName = lambda pattern, string: pattern == string
        if description and description[0] == '&':
            description = re.compile(description[1:], re.DOTALL)
            cmpDesc = matchString
        else:
            cmpDesc = lambda pattern, string: pattern == string
        if text and text[0] == '&':
            text = re.compile(text[1:], re.DOTALL)
            cmpText = matchString
        else:
            cmpText = lambda pattern, string: pattern == string
        i = 0
        for a11y, obj, path in provider(a11y, obj, path):
            if index is not None and index != path.index():
                continue
            if obj is None:
                if name is not None and not cmpName(name, a11y.name):
                    continue
                if count is not None and a11y.countChildren() != count:
                    continue
            else:
                if name is not None and not cmpName(name, a11y.getName(obj)):
                    continue
                if (description is not None and not
                    cmpDesc(description, a11y.getDescription(obj))):
                    continue
                if role is not None and a11y.getRoleName(obj) != role:
                    continue
                if count is not None and a11y.countChildren(obj) != count:
                    continue
                if action is not None:
                    found = False
                    for act in a11y.actionNames(obj):
                        if action == act:
                            found = True
                            break
                    if not found:
                        continue
                if relation is not None:
                    found = False
                    for rel in a11y.relationNames(obj):
                        if relation == rel:
                            found = True
                            break
                    if not found:
                        continue
                if (state is not None and not
                    a11y.inState(obj, getattr(a11y.stateset, state, None))):
                    continue
                if text is not None and not cmpText(text, a11y.getText(obj)):
                    continue
            i += 1
            if nth < i:
                processor.cache = (a11y, obj, path)
                return True, dumpAccessible(a11y, obj, path, depth=0, name=True,
                                        description=True, role=True, count=True,
                                        position=True, size=True, text=True,
                                        value=True, actions=True, states=True,
                                        attributes=True, relations=True)
    except:
        log.exception("Search an accessible of specified parmaters error")
        # Reset the processor cache before leaving
        processor.cache = None
        return False, Accessible(path)
    log.info("Search an accessible of specified parmaters failure")
    return False, Accessible(path)


def accessibilityPutText(processor, path, text):
    '''
    Sets the given text in an accessible of the given path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of the accessible
    :type path: tadek.core.accessible.Path
    :param text: New text of the accessible
    :type text: string
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if obj is None:
            log.warning("Attempt of setting text for non-accessible")
            return False
        status = a11y.setText(obj, text)
    except:
        log.exception("Set accessible text error: %s" % path)
        # Reset the processor cache before leaving
        processor.cache = None
        return False
    if not status:
        log.info("Set accessible text failure: %s" % path)
    return status


def accessibilityPutValue(processor, path, value):
    '''
    Sets the given value in an accessible of the given path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of the accessible
    :type path: tadek.core.accessible.Path
    :param value: New value of the accessible
    :type value: float
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if obj is None:
            log.warning("Attempt of setting value for non-accessible")
            return False
        status = a11y.setValue(obj, value)
    except:
        log.exception("Set accessible value error: %s" % path)
        # Reset the processor cache before leaving
        processor.cache = None
        return False
    if not status:
        log.info("Set accessible value failure: %s" % path)
    return status


def accessibilityExecAction(processor, path, action):
    '''
    Executes the specified action of an accessible given by the path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of the accessible
    :type path: tadek.core.accessible.Path
    :param action: An accessible action to execute
    :type action: string
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if obj is None:
            log.warning("Attempt of executing action of non-accessible")
            return False
        if action == A11Y_ACTION_FOCUS:
            status = a11y.grabFocus(obj)
        else:
            status = a11y.doAction(obj, getattr(a11y.actionset, action, action))
    except:
        log.exception("Execute accessible action error: %s" % path)
        # Reset the processor cache before leaving
        processor.cache = None
        return False
    if not status:
        log.info("Execute accessible action failure: %s" % path)
    return status

def accessibilityExecKeyboard(processor, path, keycode, modifiers):
    '''
    Generates a keyboard event for the given key code using the specified
    modifiers for an accessible of the given path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of the accessible
    :type path: tadek.core.accessible.Path
    :param keycode: A code of a key to generate event of
    :type keycode: integer
    :param modifiers:  A list of key codes to use as modifiers
    :type modifiers: list
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if a11y is None:
            log.warning("Attempt of generating keyboard"
                        " event on non-accessible")
            return False
        a11y.keyboardEvent(keycode, modifiers)
    except:
        log.exception("Generate keyboard event error: %s" % path)
        # Reset the processor cache before leaving
        processor.cache = None
        return False
    return True


def accessibilityExecMouse(processor, path, event, button, coordinates):
    '''
    Generates the given mouse event on an accessible of the specified path
    at the given coordinates using the specified mouse button.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path of the accessible
    :type path: tadek.core.accessible.Path
    :param event: A mouse event to generate
    :type event: string
    :param button: A mouse button to use
    :type button: string
    :param coordinates: A a mouse event coordinates
    :type coordinates: list
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    try:
        # Get object from the processor cache or from the accessible provider
        if processor.cache and processor.cache[-1] == path:
            a11y, obj, path = processor.cache
        else:
            a11y, obj = providers.accessible(path)
        # Reset the processor cache
        processor.cache = None
        if a11y is None:
            log.warning("Attempt of generating mouse event on non-accessible")
            return False
        button = getattr(a11y.buttonset, button, button)
        if event == 'CLICK':
            a11y.mouseClick(button=button, *coordinates)
        elif event == 'DOUBLE_CLICK':
            a11y.mouseDoubleClick(button=button, *coordinates)
        elif event == 'PRESS':
            a11y.mousePress(button=button, *coordinates)
        elif event == 'RELEASE':
            a11y.mouseRelease(button=button, *coordinates)
        elif event == 'ABSOLUTE_MOTION':
            a11y.mouseAbsoluteMotion(*coordinates)
        elif event == 'RELATIVE_MOTION':
            a11y.mouseRelativeMotion(*coordinates)
        else:
            log.warning("Unknown mouse event: %s", event)
            return False
    except:
        log.exception("Generate mouse event failure: %s" % path)
        # Reset the processor cache before leaving
        processor.cache = None
        return False
    return True

# SYSTEM

def systemGet(processor, path):
    '''
    Gets content data of a system file of the given path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path to the system file
    :type path: string
    :return: The file content data or None
    :rtype: string
    '''
    log.debug(str(locals()))
    # Reset the processor cache
    processor.cache = None
    if not os.path.exists(path):
        log.warning("Attempt of getting not existing system file: %s" % path)
        return False, ''
    fd = None
    try:
        fd = open(path, 'r')
        data = fd.read()
    except:
        log.exception("Get system file failure: %s" % path)
        return False, ''
    finally:
        if fd:
            fd.close()
    return True, data

def systemPut(processor, path, data):
    '''
    Puts the given data in a system file of the specified path.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param path: A path to the system file
    :type path: string
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    log.debug(str(locals()))
    # Reset the processor cache
    processor.cache = None
    fd = None
    try:
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            log.info("Create intermediate directories of file path: %s" % path)
            os.makedirs(dir)
        fd = open(path, 'w')
        fd.write(data)
    except:
        log.exception("Get system file failure: %s" % path)
        return False
    finally:
        if fd:
            fd.close()
    return True

def systemExec(processor, command, wait=True):
    '''
    Executes the given system command.

    :param processor: A processor object calling the function
    :type processor: Processor
    :param command: A cammand to execute
    :type command: string
    :param wait: If True wait for termination of a command process
    :type wait: boolean
    :return: The command execution status, output and error
    :rtype: tuple
    '''
    log.debug(str(locals()))
    # Reset the processor cache
    processor.cache = None
    stdout, stderr = '', ''
    try:
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
        status = True
        if wait:
            code = cmd.wait()
            log.info("System command '%s' returned with code: %d"
                     % (command, code))
            status = (code == 0)
            stdout, stderr = cmd.communicate()
            stdout = stdout or ''
            stderr = stderr or ''
    except:
        log.exception("Execute system command failure: %s" % command)
        return False, stdout, stderr
    return status, stdout, stderr

