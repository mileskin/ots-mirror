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
Distribution of Tasks to Workers
"""

#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401


import logging
import sys
import pickle
import socket
import errno

from amqplib import client_0_8 as amqp

from ots.common.dto.api import TaskCondition
from ots.common.dto.api import CommandMessage, StateChangeMessage
from ots.common.dto.api import DTO_SIGNAL
from ots.common.amqp.api import pack_message, unpack_message
from ots.common.amqp.api import testrun_queue_name

from ots.server.distributor.task import Task
from ots.server.distributor.queue_exists import queue_exists
from ots.server.distributor.timeout import Timeout
from ots.server.distributor.exceptions import OtsQueueDoesNotExistError


LOGGER = logging.getLogger(__name__)

class TaskRunnerException(Exception):
    """TaskRunnerException"""
    pass

####################################
# AMQP Queue Helpers
####################################

OTS_TESTRUN = "ots_testrun"


def _init_queue(channel, queue, exchange, routing_key):
    """
    Initialise a durable queue and a direct exchange
    with a routing_key of the name of the queue

    @type channel: C{amqplib.client_0_8.channel.Channel}  
    @param channel: The AMQP channel

    @rtype queue: C{string}  
    @return queue: The queue name
    """
    LOGGER.debug("Inititalising queue '%s', exchange '%s', routing_key '%s'"
                 %(queue, exchange, routing_key))
    channel.queue_declare(queue = queue, 
                          durable = False, 
                          exclusive = False,
                          auto_delete=True)
    channel.exchange_declare(exchange = exchange,
                             type = 'direct',
                             durable = False,
                             auto_delete = True)
    channel.queue_bind(queue = queue,
                       exchange = exchange,
                       routing_key = routing_key)


##########################
# TaskRunner
##########################

class TaskRunner(object):
    """
    Allows Tasks to be run remotely as a set associated with the Testrun 
    
    Each Task is sent individually to RabbitMQ 
    Wait for all tasks to comeback.

    The TaskRunner can only be run once.

    Results from the tasks are signalled with names 
    associated with MESSAGE_TYPES.
    """

    def __init__(self, username, password, host, vhost, 
                 services_exchange, port, 
                 routing_key, testrun_id, 
                 execution_timeout, queue_timeout, controller_timeout,
                 min_worker_version = None):
        """
        @type username: C{str}
        @param username: AMQP username 

        @type password: C{str}
        @param password: AMQP password 

        @type host: C{str}
        @param host: AMQP host 

        @type vhost: C{str}
        @param vhost: AMQP vhost

        @type services_exchange: C{str}
        @param services_exchange: AMQP services exchange

        @type port: C{int}
        @param port: AMQP port (generally 5672)

        @type routing_key: C{routing_key}
        @param routing_key: AMQP routing_key (device group) 
 
        @type testrun_id: C{int}
        @param testrun_id: The testrun id

        @type execution_timeout: C{int}
        @param execution_timeout: Time out in seconds for Task execution

        @type queue_timeout: C{int}
        @param queue_timeout: Time in seconds Tasks can wait on the queue 

        @type controller_timeout: C{int}
        @param controller_timeout: The timeout for HW controllers         
        """
        #AMQP configuration
        self._username = username
        self._password = password
        self._host = host
        self._vhost = vhost
        self._services_exchange = services_exchange
        self._port = port
        #
        self._routing_key = routing_key
        self._testrun_id = testrun_id
        #
        self._init_amqp()
        #List of Tasks
        self._tasks = []
        self._is_run = False

        #
        self._min_worker_version = min_worker_version

        #timeouts
        self._execution_timeout = execution_timeout
        self._queue_timeout = queue_timeout
        self._controller_timeout = controller_timeout
        self.timeout_handler = Timeout(execution_timeout, 
                                       queue_timeout, 
                                       controller_timeout)


    #############################################
    # MESSAGE HANDLING 
    #############################################
        
    def _on_message(self, amqp_message):
        """
        Handler for AMQP messages   
        
        Two types of messages:
        
        1. Indication of state changes on the Task 
        2. Feedback from the Task itself

        State change messages trigger a state transition.
        Everything else fires a signal

        @type message: amqplib.client_0_8.basic_message.Message 
        @param message: AMQP message
        """
        msg = unpack_message(amqp_message)
        if isinstance(msg, StateChangeMessage):
            LOGGER.debug("Received state change message %s " % msg.condition)
            self._task_transition(msg)
        else:
            #The message is data. Relay using a signal
            DTO_SIGNAL.send(sender = "TaskRunner", dto = msg)
  
    def _task_transition(self, message):
        """
        Processes state change message 
        """
        if message.is_start:
            self.timeout_handler.task_started()
        task = self._get_task(message.task_id)
        task.transition(message.condition)
        if task.is_finished:
            self._tasks.remove(task)
    
    ##########################################
    # OTHER HELPERS 
    ##########################################

    def _init_amqp(self):
        """
        Make the AMQP connection. 
        Prepare a Queue
        Start Consuming 
        """
        # Disabling "Attribute defined outside __init__" because this method is
        # called from the __init__
        #pylint: disable-msg=W0201

        self._testrun_queue = testrun_queue_name(self._testrun_id)
        self._connection = amqp.Connection(host = self._host, 
                                           userid = self._username,
                                           password = self._password,
                                           virtual_host = self._vhost, 
                                           insist = False)
        self._channel = self._connection.channel()
        _init_queue(self._channel, 
                    self._testrun_queue, 
                    self._testrun_queue, 
                    self._testrun_queue)
        self._channel.basic_consume(queue = self._testrun_queue, 
                                    callback = self._on_message,
                                    no_ack = True)


    def _get_task(self, task_id):
        """
        Get the Task for the given task_id

        @type task_id: string
        @param task_id: The ID of the Task

        @rtype task: L{Task}  
        @return task: A Task
        """
        return dict([(task.task_id, task) for task in self._tasks])[task_id]
        
    def _dispatch_tasks(self):
        """
        Publish the Tasks to the RabbitMQ
        """
        self.timeout_handler.start_queue_timeout()
        for task in self._tasks:
            log_msg = "Sending command '%s' with key '%s'" \
                          % (task.command, self._routing_key)
            LOGGER.debug(log_msg)
            cmd_msg = CommandMessage(task.command, 
                                     self._testrun_queue,
                                     task.task_id,
                                     timeout = self._execution_timeout,
                                     min_worker_version = 
                                       self._min_worker_version)
            message = pack_message(cmd_msg)
            self._channel.basic_publish(message, 
                                        exchange = self._services_exchange,
                                        routing_key = self._routing_key)

    def _wait_for_all_tasks(self):
        """
        Block until all Tasks are complete
        """
        while 1:
            try:
                self._channel.wait()
            except socket.error, e:
                # interrupted system call exception need to be ignored so that
                # testruns don't fail on apache graceful restart
                if e[0] == errno.EINTR:
                    LOGGER.debug("Interrupted system call. Ignoring...")
                else:
                    raise
            if len(self._tasks) == 0:
                break
    def _close(self):
        """
        Silent close the channel and connection
        """
        try:
            LOGGER.debug("Closing down")
            self._channel.close()
            self._connection.close()
            # Fix Memory leaks
            del self._channel.callbacks
            del self._connection.channels
            del self._connection.connection
            self._connection = None
        except:
            LOGGER.debug(sys.exc_info())
            
    #####################################################
    # PUBLIC METHODS 
    #####################################################
    
    def add_task(self, command):
        """
        Add a Task to be run

        @type command: C{list} 
        @param command: The CL to be run  
        """ 
        if self._is_run:
            raise TaskRunnerException("This TaskRunner has already been run")
        self._tasks.append(Task(command, self._execution_timeout))
        
    def run(self):
        """
        Sends the Tasks to the queue
        Wait for the results to come back
        Close the connection
        """
        if self._is_run:
            raise TaskRunnerException("This TaskRunner has already been run")
        self._is_run = True 

        if not queue_exists(self._host, 
                            self._username, 
                            self._password, 
                            self._vhost, 
                            self._routing_key):
            raise OtsQueueDoesNotExistError("No queue for %s" %\
                                                (self._routing_key))
        LOGGER.debug("Sending Tasks")
        try:
            self._dispatch_tasks()
            self._wait_for_all_tasks()
            LOGGER.info("All Tasks completed")
        finally:
            LOGGER.debug("stopping...")
            self.timeout_handler.stop()
            self._close()
