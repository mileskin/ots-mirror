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
The Task Broker is the heart of the Worker.

Listen for messages containing Tasks 
from RabbitMQ and dispatch
the Tasks as (Blocking) Processes.

The simple implementation will hold as long as 
the following assumptions holding true:

1. There is only a single resource providing i/o (RabbitMQ)
2. Tasks are blocking
3. Tasks are run in Serial 
"""

#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401

import os
from time import sleep
import logging
from itertools import cycle

from ots.worker.command import Command
from ots.worker.command import SoftTimeoutException
from ots.worker.command import HardTimeoutException
from ots.worker.command import CommandFailed
from ots.common.protocol import OTSProtocol, OTSMessageIO
from ots.common.routing.routing import get_queues

LOGGER = logging.getLogger(__name__)

STOP_SIGNAL_FILE = "/tmp/stop_ots_worker"

TASK_STATE_RESPONSES = [OTSProtocol.STATE_TASK_STARTED,
                        OTSProtocol.STATE_TASK_FINISHED]

class NotConnectedError(Exception):
    """Exception raised if not connected to amqp"""
    pass

########################################
# Command Class to Function
########################################

def _start_process(command, timeout):
    """
    Starts the specified process

    @type command: string
    @param command: The CL params for the Process to be run as a Task 

    @type timeout: int
    @param timeout: The timeout to apply to the Task
    """
    task = Command(command, 
                   soft_timeout=timeout,
                   hard_timeout=timeout + 5)

    task.execute()


##############################
# TASK_BROKER

class TaskBroker(object):
    """
    Listens to a Queue of the given Routing Key.
    Pulls messages containing Tasks from AMQP 
    Dispatch the Tasks as a process
    """   
    def __init__(self, connection, device_properties):
        self._connection = connection
        self._queues = get_queues(device_properties)
        self._keep_looping = True
        self._consumer_tags = dict()

        self._task_state = cycle(TASK_STATE_RESPONSES)

    #############################################
    # AMQP CONNECTION PROPERTIES 
    #############################################

    @property 
    def channel(self):
        """amqp channel"""
        channel = self._connection.channel
        if channel is not None:
            return channel
        else:
            raise NotConnectedError()

    ##############################################
    # AMQP Configuration
    ##############################################
       
    def _consume(self):
        """
        Start consuming messages from the queue
        """
        for queue in self._queues:

            self._consumer_tags[queue] = \
                               self.channel.basic_consume(queue = queue,
                                                          callback = self._on_message)
            LOGGER.info("consume on queue: %s" % queue)
                        


    def _stop_consuming(self):
        """
        Cancel consuming from queues. This is needed for proper load balancing.
        Otherwise the server will push next task to the consumer as soon as the
        ongoing is acked.
        """
        for queue in self._queues:
            self.channel.basic_cancel(self._consumer_tags[queue])

    def _init_connection(self):
        """
        Initialise the connection to AMQP.
        Queue and Services Exchange are both durable
        """
        for queue in self._queues:
            self.channel.queue_declare(queue = queue, 
                                       durable = True,
                                       exclusive = False, 
                                       auto_delete = False)
            self.channel.exchange_declare(exchange = queue,
                                          type = 'direct', 
                                          durable = True,
                                          auto_delete = False)
            self.channel.queue_bind(queue = queue,
                                    exchange = queue,
                                    routing_key = queue)

        self.channel.basic_qos(0, 1, False)
    ###############################################
    # LOOPING / HANDLING / DISPATCHING
    ###############################################

    def _loop(self):
        """
        The main loop
        Continually listen for messages coming from RabbitMQ
        """
        LOGGER.debug("Starting main loop...")
        while self._keep_looping:
            try:
                if not self._stop_file_exists():
                    self.channel.wait()
                else:
                    self._keep_looping = False
            except Exception:
                #FIXME Check logs to see what exceptions are raised here
                LOGGER.exception("_loop() failed")
                self._try_reconnect()
        self._clean_up()
                      
    def _on_message(self, message):
        """
        The Message Handler. 
        
        @type message: amqplib.client_0_8.basic_message.Message 
        @param message: A message containing a pickled dictionary

        This turns off the connection on receipt of a message.
        Once the Task has run the connection is reestablished.

        Response Queue is kept informed of the status
        """
        LOGGER.debug("Received Message")
        self._stop_consuming()
        self.channel.basic_ack(delivery_tag = message.delivery_tag)
        command, timeout, response_queue, task_id, version = \
                                    OTSMessageIO.unpack_command_message(message)
        self._publish_task_state_change(task_id, response_queue)

        try:
            self._dispatch(command, timeout)

        except (HardTimeoutException, SoftTimeoutException):
            LOGGER.error("Process timed out")
            error_info = "Global timeout"
            error_code = "6001"
            self._publish_error_message(task_id,
                                        response_queue,
                                        error_info,
                                        error_code)

        except (CommandFailed):
            LOGGER.error("Process failed")
            error_info = "Task execution failed"
            error_code = "6002"
            self._publish_error_message(task_id,
                                        response_queue,
                                        error_info,
                                        error_code)

        finally:
            self._publish_task_state_change(task_id, response_queue)


            self._consume()

    def _dispatch(self, command, timeout):
        """
        Dispatch the Task. Currently as a Process (Blocking)
                
        @type command: string
        @param command: The CL params for the Process to be run as a Task 

        @type timeout: int
        @param timeout: The timeout to apply to the Task
        """
        if command == OTSProtocol.COMMAND_QUIT:
            self._keep_looping = False
        elif not command == OTSProtocol.COMMAND_IGNORE:

            LOGGER.debug("Running command: '%s'"%(command))
            _start_process(command = command, timeout = timeout)

    #######################################
    # HELPERS
    #######################################

    def _publish_task_state_change(self, task_id, response_queue):

        """
        Inform the response queue of the status of the Task

        @type response_queue: string
        @param response_queue: The name of the response queue 
        """
        state = self._task_state.next()
        LOGGER.debug("Task in state: '%s'"%(state))
        message = OTSProtocol.state_change_message(task_id, state)
        self.channel.basic_publish(message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)

    def _publish_error_message(self,
                               task_id,
                               response_queue,
                               error_info,
                               error_code):

        """
        Inform the response queue about an error in testrun
        (for example timeout)

        @type response_queue: string
        @param response_queue: The name of the response queue 
        """
        error_info = error_info +" (task "+str(task_id)+")"
        message = OTSMessageIO.pack_testrun_error_message(error_info,
                                                          error_code)
        self.channel.basic_publish(message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)

        
    def _try_reconnect(self):
        """
        A poorly implemented reconnect to AMQP
        """
        #FIXME: Move out into own connection module.
        #Implement with a exponential backoff with max retries.
        LOGGER.exception("Error. Waiting 5s then retrying")
        sleep(5)
        try:
            LOGGER.info("Trying to reconnect...")
            self._connection.connect()
            self._init_connection()
            self._consume()
        except Exception:
            #If rabbit is still down, we expect this to fail
            LOGGER.exception("Reconnecting failed...")

    def _clean_up(self):
        """
        Delegate to connection cleanup
        """
        try:
            self._stop_consuming()
        except:
            pass
        if self._connection:
            self._connection.clean_up()

    def __del__(self):
        """
        Destructor
        """
        self._clean_up()

    @staticmethod
    def _stop_file_exists():
        """
        Check whether the stop file is in place
        
        @rtype stop: C{bool} 
        @return stop: Is stop file present
        """
        stop = False
        if os.path.exists(STOP_SIGNAL_FILE):
            os.system("rm -fr "+STOP_SIGNAL_FILE)
            LOGGER.info("Worker was asked to stop after testrun ready.")
            stop = True
        return stop

      
    ################################
    # PUBLIC METHODS
    ################################
        
    def run(self):
        """ 
        Polls RabbitMQ for Task Messages and runs the Tasks.

        Initialises the AMQP connections and run the forever loop.
        """
        self._init_connection()
        self._consume()
        self._loop()
