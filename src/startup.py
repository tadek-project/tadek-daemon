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
import subprocess

from tadek.core import log

SCRIPTS_DIR = "/etc/tadek/startup"

class ScriptError(Exception):
    '''
    A class of exceptions raised when a daemon start-up script run by
    runAllScripts(check=True) returns a non-zero exit status.
    '''
    _MSG_FORMAT = "Start-up script '%s' returned non-zero exit status: %d"

    def __init__(self, script, status):
        Exception.__init__(self, self._MSG_FORMAT % (script, status))
        self.script = script
        self.status = status


def runScript(script):
    '''
    Runs a start-up script of the given name.

    :param script: A name of a start-up script to run
    :type script: string
    :return: A return code of a run start-up script
    :rtype: integer
    '''
    log.debug(locals())
    script = os.path.join(SCRIPTS_DIR, script)
    if os.path.isfile(script):
        return subprocess.call(["/bin/sh", script])
    return 1

def iterScripts():
    '''
    An iterator that yields a name of one start-up script per iteration.

    :return: A name of a start-up script
    :rtype: string
    '''
    log.debug(locals())
    if os.path.isdir(SCRIPTS_DIR):
        scripts = os.listdir(SCRIPTS_DIR)
        scripts.sort()
        for script in scripts:
            yield script

def runAllScripts(check=False):
    '''
    Runs all available start-up scripts. If check is True and some script
    returns non-zero exit status when a ScriptError exception is raised.

    :param check: If True a ScriptError exception is raised if a start-up
        script returns non-zero exit status
    :type check: boolean
    :return: A number of run start-up scripts
    :rtype: integer
    '''
    log.debug(locals())
    count = 0
    for script in iterScripts():
        status = runScript(script)
        if check and status != 0:
            raise ScriptError(script, status)
        count += 1
    return count

