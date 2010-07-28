# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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
This is the server for the worker itself.
It sets up a queue and waits for jobs to process
"""

import sys
import os
from time import sleep
from os import kill, setpgrp
from pickle import loads
import logging
from amqplib import client_0_8 as amqp
from ots.worker.command import Command, SoftTimeoutException, \
    HardTimeoutException, CommandFailed


logger = logging.getLogger(__name__)

STOP_SIGNAL_FILE = "/tmp/stop_ots_worker"

class Server(object):
    """
    The OTS server. Listens for and processes messages to run jobs
    """

    _flag_no_respond = False
    
    def __init__(self, connection, client, **flags):
        """
        Store the variables passed to the object
        """
        
        # These are actually method refs to avoid having circular dependencies
        self._connection = connection
        self._client = client
        
        allowed_flags = ['no_respond']
        for (key, val) in flags.iteritems():
            if key in allowed_flags:
                setattr(self, '_flag_' + key, val)

    def start(self, *args):
        """
        Set up the server and then run it
        """
        self._setup()
        self._work_loop()

    def _setup(self):
        """
        Set up queues and exchanges and mark ourselves as a consumer
        """
        self._declare()
        self._consume()

    def _consume(self):
        """
        Tell amqplib we want to consume messages from the queue
        """
        logger.debug("In consume")
        #alias to fit within 80 char gutter
        conf = self._connection.config
        #Make sure we aren't receiving more than one message at a time
        self._connection.basic_qos(0, 1, False)
        self._connection.basic_consume(queue = conf('queue'), 
                                       callback = self._on_message)
       
    def _declare(self):
        """
        Declare:
        - a durable queue
        - a durable services exchange
        Bind:
        - queue to exchange via routing key
        """
        conf = self._connection.config
        self._connection.queue_declare(queue = conf('queue'), 
                                       durable = True,
                                       exclusive = False, 
                                       auto_delete = False)
        self._connection.exchange_declare(exchange = conf('services_exchange'),
                                          type = 'direct', 
                                          durable = True,
                                          auto_delete = False)
        self._connection.queue_bind(queue = conf('queue'),
                                    exchange = conf('services_exchange'),
                                    routing_key = conf('routing_key'))

                                    
    def _work_loop(self):
        """
        Keep listening and processing messages
        """

        conf = self._connection.config
       
        keep_looping = True
        while keep_looping:
            try:
                if os.path.exists(STOP_SIGNAL_FILE):
                    os.system("rm -fr "+STOP_SIGNAL_FILE)
                    logger.info("Worker was asked to stop after testrun ready.")
                    raise SystemExit

                logger.debug("Waiting for a message on queue '%s'..."
                        % (self._connection.config('queue')))
                self._connection.wait()
            except SystemExit:
                # Stop SystemExit being caught by the catch-all below
                logger.debug('Caught SystemExit, Initiating Shutdown')
                self.stop()
                keep_looping=False
            except Exception, e:
                logger.exception("Error. Waiting 5s then retrying")
                sleep(5)
                try:
                    logger.info("Trying to reconnect...")
                    self._connection.connect()
                    self._setup()
                except Exception, e:
                    #If rabbit is still down, we expect this to fail
                    logger.exception("Reconnecting failed...")



    def _deserialise(self, thing):
        """
        Deserialise the object sent from OTS distributor
        """
        return loads(thing)
        
    def _client_send(self, queue, message): #TODO ADD task_id to message!!!
        """
        Sends a message back to the client
        """
        #Allows you to turn off responses for tests
        if not self._flag_no_respond:
            self._client.send_message(queue,queue,message)
            
    def _on_message(self, message):
        """
        Called back when we have a message
        """
        conf = self._connection.config
        body = self._deserialise(message.body)
        command = " ".join(body["command"])
        response_queue = body["response_queue"]
        task_id = body["task_id"]
        timeout = body.get('timeout', 60)

        logger.debug('Received message: ' + command)
        self._connection.basic_cancel()
        self._connection.basic_ack(delivery_tag=message.delivery_tag) 

        #By default, send a response
        _send_response = True
        # Tell the distributor we've started
        self._client_send(response_queue, 'started')
        try:
            if command == 'quit':
                raise SystemExit
            elif command == 'ignore':
                pass
            else:
                self._start_process(command = command, timeout = timeout)
        except (HardTimeoutException, SoftTimeoutException):
            _send_response = False
            logger.exception("Process timed out")
        except Exception, e:
            logger.exception("Unexpected exception")
        finally:
            #Tell the distributor we're finished
            if _send_response:
                self._client_send(response_queue, 'finished')

            self._connection.basic_consume(queue = conf('queue'),
                                           callback = self._on_message)


    def _start_process(self, command, timeout):
        """
        Starts the specified process
        """
        self.task = Command(command,
                            soft_timeout=timeout,
                            hard_timeout=timeout+5)
        
        logger.debug("Started process '%s', pid '%i'" \
                         % (command, self.task.pid))
        self.task.execute()
        logger.debug(
            "Finished running command '%s'. Return code: '%s', output: '%s'"
            % (command, self.task.return_value, self.task.stdout))


    def stop(self):
        """
        Shuts down the connection, cleans up etc.
        """
        try:
            logger.debug("Stopping service")
            self._connection.cleanup()
            logger.debug("Quitting")
        except:
            #Assume we weren't connected. Not a lot we can do here anyway
            pass
        
    def __del__(self):
        """
        Destructor. Clean up
        """
        self.stop()
