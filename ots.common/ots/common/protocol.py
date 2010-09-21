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
Module implements OTS protocol and message io handling
"""

import logging
from pickle import dumps, loads
from amqplib import client_0_8 as amqp

import ots.common
from ots.common.resultobject import ResultObject

LOGGER = logging.getLogger(__name__)


def get_version():
    """
    Returns version of OTSProtocol
    """
    return ots.common.__VERSION__

def _pack_message(message, delivery_mode):
    """Packs the message with Pickle"""
    message = dumps(message, True) # Use binary mode because binary files can be
                                   # sent as result messages
    message = amqp.Message(message)
    message.properties['delivery_mode'] = delivery_mode
    return message

def _unpack_message(message):
    """Unpack the message with Pickle"""
    body = loads(message.body)
    LOGGER.debug("Unpickled Message: %s" % (body))
    return body

class OTSProtocolException(Exception):
    """"OTSProtocolException"""
    pass

class OTSProtocol(object):
    """
    This class defines the communication protocol between OTS workers and 
    OTS server.
    """

    STATE_TASK_STARTED = 'started'
    STATE_TASK_FINISHED = 'finished'

    COMMAND_QUIT = 'quit'
    COMMAND_IGNORE = 'ignore'
    COMMAND = 'command'

    VERSION = 'version' # The Protocol Version
    ERROR_INFO = 'error_info'
    ERROR_CODE = 'error_code'
    MESSAGE_TYPE = 'message_type'
    STATE = 'state'
    STATUS_INFO = 'status_info'
    ENVIRONMENT = 'environment'
    PACKAGES = 'packages'
    RESULT = 'result'
    MIN_WORKER_VERSION = 'min_worker_version'
    RESPONSE_QUEUE = 'response_queue'
    TIMEOUT = 'timeout'

    # Different types of messages
    STATE_CHANGE = 'STATE_CHANGE'
    RESULT_OBJECT = 'RESULT_OBJECT'
    TESTRUN_STATUS = 'TESTRUN_STATUS'
    TESTRUN_ERROR = 'TESTRUN_ERROR'
    TESTPACKAGE_LIST = 'TESTPACKAGE_LIST'

    STATUS = 'status'
    TASK_ID = 'task_id'

    @staticmethod
    def state_change_message(task_id, status):
        """
        @type task_id: C{int}
        @param task_id: The ID of the task

        @type status: C{string}
        @param status: STATE_TASK_STARTED or STATE_TASK_FINISHED

        @rtype message: amqplib.client_0_8.basic_message.Message
        @return message: A pickled message
        """
        message = dict(version = get_version(),
                       message_type="STATE_CHANGE",
                       task_id = task_id,
                       status = status)
        return amqp.Message(dumps(message))


MESSAGE_FORMATS = {OTSProtocol.STATE_CHANGE: (OTSProtocol.TASK_ID,
                                              OTSProtocol.STATUS),
                   OTSProtocol.RESULT_OBJECT: OTSProtocol.RESULT,
                   OTSProtocol.TESTRUN_STATUS: [OTSProtocol.STATE, OTSProtocol.STATUS_INFO],
                   OTSProtocol.TESTRUN_ERROR: [OTSProtocol.ERROR_INFO, 
                                               OTSProtocol.ERROR_CODE],
                   OTSProtocol.TESTPACKAGE_LIST :[OTSProtocol.ENVIRONMENT, OTSProtocol.PACKAGES]}
