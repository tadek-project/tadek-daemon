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
import locale

from tadek.core import log
from tadek.core import config
from tadek.connection import run
from tadek.connection import server
from tadek.connection import protocol

import handler
import startup

#: Default IP address of daemons
DEFAULT_IP = '0.0.0.0'
#: Default port number of daemons
DEFAULT_PORT = 8089

class Daemon(server.Server):
    '''
    A daemon class responsible for server connection and handling client
    connections.
    '''
    handlerClass = handler.DaemonHandler

    def __init__(self, conf=None):
        '''
        Initializes daemon by starting and configuring a server.

        :param conf: A path to a daemon configuration file
        :type conf: string
        '''
        if conf is not None:
            if os.path.isfile(conf):
                config.update('daemon', conf)
            else:
                log.warning("Configuration file %s does not exist."
                            " Skipped" % conf)
        port = config.getInt('daemon', 'connection', 'port')
        ip = config.get('daemon', 'connection', 'address')
        if ip is None:
            log.warning("No attribute IP in daemon configuration file. "
                        "Using default value %s" % DEFAULT_IP)
            config.set('daemon', 'connection', 'address', DEFAULT_IP)
            ip = DEFAULT_IP
        if port is None:
            log.warning("No attribute port in daemon configuration file. "
                        "Using default value %d" % DEFAULT_PORT)
            config.set('daemon', 'connection', 'port', DEFAULT_PORT)
            port = DEFAULT_PORT
        server.Server.__init__(self, (ip, port))
        info = protocol.create(protocol.MSG_TYPE_RESPONSE,
                               protocol.MSG_TARGET_SYSTEM,
                               protocol.MSG_NAME_INFO,
                               version=config.VERSION,
                               locale=(locale.getdefaultlocale()[0] or ''),
                               extensions=protocol.getExtensions(),
                               status=True)
        self._infoData = info.marshal()

    def handle_accept(self):
        '''
        Sends an information response to an accepted client.
        '''
        try:
            handler = server.Server.handle_accept(self)
        except:
            log.exception("Error while accepting connection")
        else:
            handler.push(''.join([self._infoData, handler.get_terminator()]))

    def onClose(self):
        '''
        Function called when socket is closed.
        '''
        log.info("Daemon stopped running")

    def onError(self, exception):
        '''
        Function called when exception is raised.

        :param exception: An exception to handle
        :type exception: Exception
        '''
        log.exception(exception)

    def run(self):
        '''
        Starts asyncore.loop().
        '''
        log.info("Starting daemon at %s:%d" % self.address)
        run()


def runScripts():
    '''
    Runs all daemon start-up scripts and checks they return status.
    '''
    log.debug(locals())
    print "Running start-up scripts (if any)..."
    n = 0
    try:
        n = startup.runAllScripts(check=True)
    except startup.ScriptError, err:
        print >> sys.stderr, ("Error code was returned by start-up script: "
                              "%s" % err.script)
        print >> sys.stderr, " !!! Daemon starting halted !!!"
        sys.exit(1)
    print "Running start-up scripts finished...",
    if n == 0:
        print "No scripts ran"
    elif n == 1:
        print "One script ran"
    else:
        print "%d scripts ran" % n
    print

def main(conf=None, startup=True):
    '''
    Runs a daemon.

    :param conf: A path to daemon configuration file
    :type conf: string
    '''
    log.debug(locals())
    if startup:
        runScripts()
    try:
        d = Daemon(conf)
    except:
        msg = "Daemon starting failure"
        print >> sys.stderr, msg
        log.exception(msg)
        sys.exit(1)
    print "Daemon is running at %s:%d" % d.address
    d.run()

