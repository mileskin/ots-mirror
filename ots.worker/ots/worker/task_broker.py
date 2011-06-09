# ***** BEGIN LICENCE BLOCK *****

# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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

#pylint: disable=E0611
#pylint: disable=F0401

import os
from time import sleep
import logging
from socket import gethostname
from itertools import cycle

from ots.common.amqp.api import unpack_message, pack_message
from ots.common.dto.api import StateChangeMessage, TaskCondition, Monitor
from ots.common.dto.api import MonitorType
from ots.common.routing.api import get_queues

from ots.worker.version import __VERSION__
from ots.worker.command import Command
from ots.worker.command import CommandFailed
from ots.common.dto.ots_exception import OTSException
from ots.worker.conductor.helpers import get_logger_adapter

STOP_SIGNAL_FILE = "/tmp/stop_ots_worker"

TASK_CONDITION_RESPONSES = [TaskCondition.START,
                            TaskCondition.FINISH]

class NotConnectedError(Exception):
    """Exception raised if not connected to amqp"""
    pass

########################################
# Command Class to Function
########################################

def _start_process(command):
    """
    Starts the specified process

    @type command: C{str}
    @param command: The CL params for the Process to be run as a Task 
    """
    task = Command(command)
    task.execute()


##############################
# TASK_BROKER
##############################

class TaskBroker(object):
    """
    Listens to a Queue of the given Routing Key.
    Pulls messages containing Tasks from AMQP 
    Dispatch the Tasks as a process
    """   
    def __init__(self, connection, device_properties):
        """
        device_properties have magic keys that
        are dependent on the rules set out 
        in ots.common.routing.routing 

        @type connection : L{ots.worker.connection.Connection} 
        @param connection : The connection 

        @type device_properties : C{dict}
        @param device_properties : The device_properties
        """
        self._log = get_logger_adapter(__name__)
        self._connection = connection
        self._queues = get_queues(device_properties)
        self._keep_looping = True
        self._consumer_tags = dict()

        self._task_state = cycle(TASK_CONDITION_RESPONSES)
        self._amqp_log_handler = None
        self._xml_file = None

    ############################################
    # LOG HANDLER
    ############################################

    def _set_amqp_log_handler(self, amqp_log_handler):
        """
        @type amqp_log_handler : L{AMQPLogHandler}
        @param amqp_log_handler: The AMQP Log Handler
        """
        self._amqp_log_handler = amqp_log_handler
        self._amqp_log_handler.channel = self.channel

    amqp_log_handler = property(None, _set_amqp_log_handler)

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
    def _start_consume(self):
        """
        Start consuming messages from the queue
        """
        basic_consume = self.channel.basic_consume
        for queue in self._queues:
            self._log.info("start consume on queue: %s" % queue)
            self._consumer_tags[queue] = basic_consume(queue = queue,
                                              callback = self._on_message)
            
    def _stop_consume(self):
        """
        Cancel consuming from queues. This is needed for proper load balancing.
        Otherwise the server will push next task to the consumer as soon as the
        ongoing is acked.
        """
        for queue in self._queues:
            self.channel.basic_cancel(self._consumer_tags[queue])
            self._log.info("stop consume on queue: %s" % queue)

    def _init_connection(self):
        """
        Initialise the connection to AMQP.
        Queue and Services Exchange are both durable
        """
        for queue in self._queues:
            self._log.info("Initialising queue: %s" % queue)
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
        self._log.debug("Starting main loop...")
        while self._keep_looping:
            try:
                if not self._stop_file_exists():
                    self.channel.wait()
                else:
                    self._keep_looping = False
            except Exception:
                self._log.exception("_loop() failed")
                self._try_reconnect()
        self._clean_up()
    
    def _handle_message(self, message):
        """
        The Message Handler. 
        
        @type message: amqplib.client_0_8.basic_message.Message 
        @param message: A message containing a pickled dictionary

        This turns off the connection on receipt of a message.
        Once the Task has run the connection is reestablished.

        Response Queue is kept informed of the status
        """
        
        self._stop_consume()
        self.channel.basic_ack(delivery_tag = message.delivery_tag)
        #
        cmd_msg = unpack_message(message)
        task_id = cmd_msg.task_id
        response_queue = cmd_msg.response_queue
        self._set_log_handler(response_queue)
        self._publish_task_state_change(task_id, response_queue)
        #
        try:
            self._dispatch(cmd_msg)
        except CommandFailed, exc:
            error_msg = "Command %s failed" % cmd_msg.command
            self._log.error(error_msg)

            # We need to send pure OTSException because server does not know
            # about ots.worker.command.CommandFailed and unpickle will fail
            exception = OTSException(exc.errno, error_msg)
            exception.task_id = task_id
            self._publish_exception(task_id,
                                    response_queue,
                                    exception)
        finally:
            self._set_log_handler(None)
            self._publish_task_state_change(task_id, response_queue)
            if self._keep_looping:
                self._start_consume()

    def _on_message(self, message):
        """
        The High Level Message Handler. 
        Handles messages if the Worker is version compatible 
        
        @type message: amqplib.client_0_8.basic_message.Message 
        @param message: A message containing a pickled dictionary
        """
        self._log.debug("Received Message")
        if self._is_version_compatible(message):
            self._handle_message(message)
        else:
            self._log.error("Worker not version compatible")
            #Close the connection makes message available to other Workers
            self._clean_up()

    def _dispatch(self, cmd_msg):
        """
        Dispatch the Task. Currently as a Process (Blocking)
                
        @type cmd_msg: C{ots.common.amqp.messages.CommandMessage}
        @param cmd_msg: The CL params for the Process to be run as a Task 
        """

        if cmd_msg.is_quit:
            self._log.debug("Received QUIT command")
            self._keep_looping = False
        elif not cmd_msg.is_ignore:
            
            command = cmd_msg.command
            
            self._xml_file = None
            
            if cmd_msg.xml_file is not None:
                self._save_xml_file(cmd_msg.xml_file)
            
            self._log.debug("Running command: '%s'"%(command))
            _start_process(command = command)
            self._remove_xml_file()
    
    ########################################
    # MESSAGE PUBLISHING
    ########################################

    def _publish_task_state_change(self, task_id, response_queue):

        """
        Inform the response queue of the status of the Task

        @type response_queue: string
        @param response_queue: The name of the response queue 
        """
        state = self._task_state.next()
        self._log.debug("Task in state: '%s'"%(state))

        # Monitor event send
        event_type = MonitorType.TASK_ONGOING
        if state == TaskCondition.FINISH:
            event_type = MonitorType.TASK_ENDED
        monitor_event = Monitor(event_type,
                                gethostname(),
                                task_id)

        amqp_message = pack_message(monitor_event)
        self.channel.basic_publish(amqp_message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)

        state_msg = StateChangeMessage(task_id, state)
        amqp_message = pack_message(state_msg) 
        self.channel.basic_publish(amqp_message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)
        
        
    def _publish_exception(self, task_id, response_queue, exception):
        """
        Put an Exception on the response queue 
        and move the Task onto the next state

        @type response_queue: C{str}
        @param response_queue: The name of the response queue 

        @type exception: L{OTSException}
        @param exception: An OTSException 

        """
        self._log.debug("publishing exception")
        message = pack_message(exception)
        try:
            self.channel.basic_publish(message,
                                       mandatory = True,
                                       exchange = response_queue,
                                       routing_key = response_queue)
        except AMQPChannelException:
            self._log.error("Can't publish exception")

    #######################################
    # HELPERS
    #######################################

    def _is_version_compatible(self, message):
        """
        Is the Worker version compatible

        @type message: amqplib.client_0_8.basic_message.Message 
        @param message: A message containing a pickled dictionary

        @rtype: C{bool}
        @return: Returns True if compatible otherwise false
        """
        ret_val = True
        cmd_msg = unpack_message(message)
        min_worker_version = cmd_msg.min_worker_version

        if min_worker_version is not None:
            version = __VERSION__.split(".", 3)
            major_version = version[0] + "." + version[1]
            self._log.debug("Min version: %s. Worker version: %s"%
                         (min_worker_version, major_version))
            ret_val = float(major_version) >= float(min_worker_version)
        return ret_val

    def _set_log_handler(self, queue):
        """
        Set the AMQP Log Handler to use the queue
        or None to stop it logging

        @type queue : C{str} or None
        @param queue : The name of the queue 
        """
        if self._amqp_log_handler is not None:
            self._amqp_log_handler.queue = queue
            self._amqp_log_handler.exchange = queue
        
    def _try_reconnect(self):
        """
        A poorly implemented reconnect to AMQP
        """
        #Implement with a exponential backoff with max retries.
        self._log.exception("Error. Waiting 5s then retrying")
        sleep(5)
        try:
            self._log.info("Trying to reconnect...")
            self._connection.connect()
            self._init_connection()
            self._start_consume()
        except Exception:
            #If rabbit is still down, we expect this to fail
            self._log.exception("Reconnecting failed...")

    def _clean_up(self):
        """
        Delegate to connection cleanup
        """
        try:
            self._stop_consume()
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
        
        @rtype: C{bool} 
        @return: Is stop file present
        """
        stop = False
        if os.path.exists(STOP_SIGNAL_FILE):
            os.system("rm -fr "+STOP_SIGNAL_FILE)
            self._log.info("Worker was asked to stop after testrun ready.")
            stop = True
        return stop
    
    def _save_xml_file(self, xml_io):
        """
        Store the xml file to the system
        @type xml_io: C{StringIO} 
        @param xml_io: XML file
        """
        
        if xml_io is not None:
            self._xml_file = os.path.join("/tmp/", xml_io.name)
            xml_fb = open(self._xml_file, 'w')
            xml_fb.write(xml_io.getvalue())
            xml_fb.close()
            
            return self._xml_file
            
    
    def _remove_xml_file(self):
        """
        Remove stored xml file from the system
        """
        
        try:
            if self._xml_file is not None:
                os.remove(self._xml_file)
        except:
            self._log.warning("failed to remove test plan", exc_info = True)
      
    ################################
    # PUBLIC METHODS
    ################################
        
    def run(self):
        """ 
        Polls RabbitMQ for Task Messages and runs the Tasks.

        Initialises the AMQP connections and run the forever loop.
        """
        self._init_connection()
        self._start_consume()
        self._loop()
