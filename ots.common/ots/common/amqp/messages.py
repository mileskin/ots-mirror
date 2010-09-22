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

#WIP needs further simplification just cleaning the slate 

"""
The Message Types for sending down the wire and 
the methods for packing and unpacking them
"""

from pickle import dumps, loads

from amqplib import client_0_8 as amqp

import ots.common
from ots.common.datatypes.resultobject import ResultObject

DELIVERY_MODE = 2

#########################
# PACK / UNPACK
#########################

def unpack_message(message):
    """
    Unpack the message with Pickle

    @type message: amqplib.client_0_8.basic_message.Message
    @param message: A pickled message in AMQP message format

    @rtype message: L{ots.common.message_io.Message} 
    @rparam mesage: The Message 
    """
    body = loads(message.body)
    return body

def pack_message(message):
    """
    Packs the message for sending as AMQP with Pickle

    @type message: L{ots.common.message_io.Message} 
    @param mesage: The AMQP message 

    @rtype message: amqplib.client_0_8.basic_message.Message
    @return message: A pickled message in AMQP message format
    """
    message = dumps(message, True)
    amqp_message = amqp.Message(message)
    amqp_message.properties['delivery_mode'] = DELIVERY_MODE
    return amqp_message

##############################
# TASK CONDITION
##############################

class TaskCondition(object):

    START = 'start'
    FINISH = 'finish'


##############################
# MESSAGE TYPES 
##############################

class Message(object):
    
    __version__ = ots.common.__VERSION__

class CommandMessage(Message):

    QUIT = 'quit'
    IGNORE = 'ignore'

    def __init__(self, command, response_queue, task_id, 
                 timeout = 60, min_worker_version = None):
        """
        @type command: C{list}
        @param command: The CL params

        @type queue : C{str}
        @param queue : The queue to post the message

        @type timeout : C{int}
        @param timeout : The timeout for the Task

        @type task_id : C{int}
        @param task_id : The Task ID

        @type min_worker_version: C{str}
        @type min_worker_version: The minimum acceptable worker version 
        """
        self.command = " ".join(command)
        self.response_queue = response_queue
        self.task_id = task_id 
        self.timeout = timeout 
        self.min_worker_version = min_worker_version

    @property    
    def is_quit(self):
        return self.command == self.QUIT

    @property 
    def is_ignore(self):
        return self.command == self.IGNORE

class StatusMessage(Message):

    def __init__(self, state, status_info):
        self.state = state
        self.status_info = status_info

class ErrorMessage(Message):
    
    def __init__(self, error_info, error_code):
        self.error_info = error_info 
        self.error_code = error_code 

class StateChangeMessage(Message):

    def __init__(self, task_id, condition):
        self.task_id = task_id 
        self.condition = condition

    @property 
    def is_start(self):
        return self.condition == TaskCondition.START

    @property
    def is_finish(self):
        return self.condition == TaskCondition.FINISH
