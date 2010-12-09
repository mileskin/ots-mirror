# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****


"""
This module encapsulates handling of server side timeouts in ots distributor
"""


import logging
import signal


#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401


from ots.server.distributor.exceptions import OtsExecutionTimeoutError
from ots.server.distributor.exceptions import OtsQueueTimeoutError

LOGGER = logging.getLogger(__name__)

class Timeout(object):
    """
    Implements ots distributor server side timeouts by using signals.
    
    Raises OtsExecutionTimeoutError if timed out during execution
    Raises OtsQueueTimeoutError if timed out before any tasks started

    """


    def __init__(self, execution_timeout, queue_timeout, controller_timeout):
        """
 
        @type execution_timeout :C{int} 
        @param execution_timeout: The timeout for remote command execution

        @type queue_timeout :C{int} 
        @param queue_timeout: The queue timeout for the start of the first task

        @type controller_timeout : C{int}
        @param controller_timeout : controller_timeout 
        """
        self.execution_timeout = execution_timeout
        self.queue_timeout = queue_timeout
        self.controller_timeout = controller_timeout

    def __del__(self):
        self.stop()
    

    def start_queue_timeout(self):
        """
        Starts queue timeout. This should be called when task messages are
        sent to queue
        """
        def queue_timeout_handler(signum, frame):
            """
            A callback that raises OtsQueueTimeoutError
            """

            # Disabling "unused argument" warning. Arguments are defined
            # by the signal module
            #
            #pylint: disable-msg=W0613

            LOGGER.error("Queue timeout")
            raise OtsQueueTimeoutError(self.queue_timeout)

        LOGGER.info("Setting queue timeout to %s minutes" \
                        % (self.queue_timeout/60))
        signal.signal(signal.SIGALRM, queue_timeout_handler)
        signal.alarm(self.queue_timeout)

    def task_started(self, single_task = False):
        """sets timeout. Previous timeout will be overwritten."""
        def execution_timeout_handler(signum, frame):
            """
            A callback that raises OtsExecutionTimeoutError
            """
            # Disabling "unused argument" warning. Arguments are defined
            # by the signal module
            #
            #pylint: disable-msg=W0613


            LOGGER.error("Execution timeout (server side)")
            raise OtsExecutionTimeoutError

        if not single_task:
            timeout = self._calculate_new_timeout()
        else:
            timeout = self.execution_timeout
        LOGGER.info("Setting server side execution timeout to %s minutes" \
                          % (timeout/60))
        signal.signal(signal.SIGALRM, execution_timeout_handler)
        signal.alarm(timeout)

    @staticmethod
    def stop():
        """Stops all timeouts."""
        signal.alarm(0)

    def _calculate_new_timeout(self):
        """
        calculates the new execution timeout.

        Because multiple tasks may need to be executed on the same worker, we
        need to give some extra time for the next task to be picked up.

        In most cases timeouts are handled on worker side. This server side
        timeout is only a final safety mechanism if for example network
        connection to worker is permanently lost.
        """
        return self.queue_timeout + self.execution_timeout \
               + self.controller_timeout
