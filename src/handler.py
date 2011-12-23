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

from tadek.core import log
from tadek.connection import protocol
from tadek.connection import server

import processor

class DaemonHandler(server.Handler):
    '''
    A class responsible for direct communication with client, receiving
    messages, processing them and sending responses.
    '''
    def __init__(self, socket, client):
        '''
        Initializes a handler and gets log.

        :param socket: Socket on which communication takes place.
        :type socket: socket
        :param client: Client address containing IP and port.
        :type client: tuple
        '''
        log.info("Accepting connection from %s on %s" % (client, socket))
        server.Handler.__init__(self, socket, client)
        log.info("Accepted connection from %s on %s" % (client, self))
        self._processor = processor.Processor()

    def push(self, data):
        '''
        Pushes the given response data to a corresponding client.

        :param data: Response data
        :type data: string
        '''
        log.debug("Sending response:\n%s", data)
        server.Handler.push(self, data)

    def onRequest(self, data):
        '''
        Processes the received request data and returns an appropriate response.

        :param data: Request data
        :type data: string
        :return: Processed request and generated response instances
        :rtype: tuple
        '''
        log.debug("Handling request:\n%s", data)
        request, response = server.Handler.onRequest(self, data)
        if response is None:
            try:
                if request.type != protocol.MSG_TYPE_REQUEST:
                    raise protocol.UnsupportedMessageError(request.type,
                                                           request.target,
                                                           request.name,
                                                           *request.getParams())
                response = self._processor(request)
            except protocol.UnsupportedMessageError, err:
                log.error(err)
            except:
                log.exception("Request processing failure")
        return request, response

    def onClose(self):
        '''
        Function called when socket is closed.
        '''
        log.info("Closing connection with %s on %s." % (str(self.client), self))

    def onError(self, exception):
        '''
        Function called when error occurs.

        :param exception: Exception to handle with.
        :type exception: Exception
        '''
        log.exception(exception)

