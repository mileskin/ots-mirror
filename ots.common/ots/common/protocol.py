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

PROTOCOL_VERSION = '0.1dev'

def get_version():
    """
    Returns version of OTSProtocol
    """
    return ots.common.get_version()

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

class MessageException(Exception):
    """"MessageException"""
    pass

class OTSMessageIO(object):
    """
    Provides methods for packing and unpacking OTS messages
    """
    # Unpack/pack methods for command messages
    ##########################################

    @staticmethod 
    def unpack_min_worker_version(message):
        """
        Get the minimum worker version

        @type message: amqplib.client_0_8.basic_message.Message
        @param message: The message
        """
        body = _unpack_message(message)
        version = body[OTSProtocol.VERSION]
        min_worker_version = body[OTSProtocol.MIN_WORKER_VERSION]
        return min_worker_version

    @staticmethod
    def unpack_command_message(message):
        """
        Unpickle the message and extract the parameters

        @type message: amqplib.client_0_8.basic_message.Message
        @param message: The message

        @rtype: C{tuple} consisting of C{list}, C{int}, C{int}
        @return: The parameters for running the task
        """
        body = _unpack_message(message)
        version = body[OTSProtocol.VERSION]
        command = " ".join(body[OTSProtocol.COMMAND])
        response_queue = body[OTSProtocol.RESPONSE_QUEUE]
        task_id = body[OTSProtocol.TASK_ID]
        timeout = body.get(OTSProtocol.TIMEOUT, 60)
        return command, timeout, response_queue, task_id, version

    @staticmethod
    def pack_command_message(min_worker_version, command, 
                             queue, timeout, task_id):
        """
        Create an AMQP message for the command

        @type min_worker_version: C{str}
        @type min_worker_version: The minimum acceptable worker version 

        @type command: C{list}
        @param command: The CL params

        @type queue : C{str}
        @param queue : The queue to post the message

        @type timeout : C{int}
        @param timeout : The timeout for the Task

        @type task_id : C{int}
        @param task_id : The Task ID

        @rtype message: amqplib.client_0_8.basic_message.Message
        @return message: AMQP message
        """
        message = {OTSProtocol.MIN_WORKER_VERSION : min_worker_version,
                   OTSProtocol.VERSION : get_version(),
                   OTSProtocol.COMMAND : command,
                   OTSProtocol.RESPONSE_QUEUE : queue,
                   OTSProtocol.TIMEOUT : timeout,
                   OTSProtocol.TASK_ID : task_id}
        return _pack_message(message, 2)

    # Unpack/pack methods for result object messages
    ################################################

    @staticmethod
    def unpack_result_message(message):
        """Unpacks elements from result object message"""
        body = _unpack_message(message)
        version = body[OTSProtocol.VERSION]
        result = body["result"]
        return result, version

    @staticmethod
    def pack_result_message(filename, content, origin,
                            test_package, environment):
        """ Create message which include ResultObject result file """
        result = ResultObject(filename,
                              content,
                              test_package,
                              origin,
                              environment)

        msg = dict()
        msg[OTSProtocol.MESSAGE_TYPE] = OTSProtocol.RESULT_OBJECT
        msg[OTSProtocol.RESULT] = result
        msg[OTSProtocol.VERSION] = get_version()
        return _pack_message(msg, 2)

    # Unpack/pack methods for testrun status messages
    #################################################

    @staticmethod
    def unpack_testrun_status_message(message):
        """Unpacks elements from testrun status message"""
        body = _unpack_message(message)
        version = body[OTSProtocol.VERSION]
        state = body[OTSProtocol.STATE]
        status_info = body[OTSProtocol.STATUS_INFO]
        return state, status_info, version

    @staticmethod
    def pack_testrun_status_message(state, status_info):
        """Create testrun state change message"""

        msg = dict()
        msg[OTSProtocol.MESSAGE_TYPE] = OTSProtocol.TESTRUN_STATUS
        msg[OTSProtocol.STATE] = state
        msg[OTSProtocol.STATUS_INFO] = status_info
        msg[OTSProtocol.VERSION] = get_version()
        return _pack_message(msg, 2)

    # Unpack/pack methods for testrun error messages
    ################################################

    @staticmethod
    def unpack_testrun_error_message(message):
        """Unpacks elements from testrun error message"""
        body = _unpack_message(message)
        error_info = body[OTSProtocol.ERROR_INFO]
        error_code = body[OTSProtocol.ERROR_CODE]
        version = body[OTSProtocol.VERSION]
        return error_info, error_code, version

    @staticmethod
    def pack_testrun_error_message(error_info, error_code):
        """Create error message"""
        msg = dict()
        msg[OTSProtocol.MESSAGE_TYPE] = OTSProtocol.TESTRUN_ERROR
        msg[OTSProtocol.ERROR_INFO] = error_info
        msg[OTSProtocol.ERROR_CODE] = error_code
        msg[OTSProtocol.VERSION] = get_version()
        return _pack_message(msg, 2)

    # Unpack/pack methods for testpackage list  messages
    ####################################################

    @staticmethod
    def unpack_testpackage_list_message(message):
        """Unpacks elements from testpackage list message"""
        body = _unpack_message(message)
        environment = body[OTSProtocol.ENVIRONMENT]
        packages = body[OTSProtocol.PACKAGES]
        version = body[OTSProtocol.VERSION]
        return environment, packages, version

    @staticmethod
    def pack_testpackage_list_message(environment, packages):
        """Create message that has list of test packages"""
        msg = dict()
        msg[OTSProtocol.MESSAGE_TYPE] = OTSProtocol.TESTPACKAGE_LIST
        msg[OTSProtocol.ENVIRONMENT] = environment
        msg[OTSProtocol.PACKAGES] = packages
        msg[OTSProtocol.VERSION] = get_version()
        return _pack_message(msg, 2)

    @staticmethod
    def unpack_message(message):
        """
        Decrypt an AMQP message into something OTS understands.
        Check the format

        @type message: amqplib.client_0_8.basic_message.Message
        @param message: AMQP message

        @rtype: C{dict}
        @return: Message data
        """
        body = loads(message.body)

        # Check message integrity
        if not isinstance(body, dict):
            err_msg = "Expected dict in message type, received %s" \
                % (type(body))
            raise MessageException(err_msg)
        if not OTSProtocol.MESSAGE_TYPE in body:
            err_msg = "Received bad message. message_type missing"
            raise MessageException(err_msg)
        if not OTSProtocol.VERSION in body:
            err_msg = "Receive bad message. version missing"
            raise MessageException(err_msg)
        if body[OTSProtocol.VERSION] != get_version():
            err_msg = "Peer uses unsupported (%s) version of OTSProtocol!" \
                % body[OTSProtocol.VERSION]

        message_type = body[OTSProtocol.MESSAGE_TYPE]
        formats =  MESSAGE_FORMATS[message_type]
        if isinstance(formats, str):
            formats = [formats]
        for msg_attr in formats:
            if not body.has_key(msg_attr):
                raise MessageException("Format error no '%s' in %s message"
                                       %(msg_attr, message_type))
        return body
