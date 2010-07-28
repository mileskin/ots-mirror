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
Client for distribution of Tasks to Workers
"""

import os
from time import sleep
import logging
import signal
import sys
from subprocess import Popen, PIPE
import re
from uuid import uuid1
from pickle import dumps
import ConfigParser
import uuid

from amqplib import client_0_8 as amqp

from ots.distributor.get_version import get_version 

logger = logging.getLogger(__name__)

#######################
# States
#######################

DISCONNECTED = 0
CONNECTED = 1
WAITING_START = 2
WAITING_END = 3

class OtsQueueDoesNotExistError(Exception):
    pass

class OtsGlobalTimeoutError(Exception):
    pass

class OtsConnectionError(Exception):
    pass

class OtsWorkerStartTimeoutError(Exception):
    def __init__(self,timeout_length,*args,**kwargs):
        self.timeout_length = timeout_length
        Exception.__init__(self, *args, **kwargs)

class Alarm(Exception):
    """
    Basic exception class to handle timeouts, per Alex Martelli's example
    """
    pass

def alarm_handler(signum, frame):
    """
    Utility function to raise Alarm(), per Alex Martelli's example
    """
    raise Alarm


#####################
# Client
####################

class Client(object):
    """
    The AMQP client.
    Tasks posted to RabbitMQ 
    """

    def __init__(self, username, password, host, vhost, services_exchange,
                 port, routing_key, timeout, testrun_id):
        """
        Initialises the class. Sets up the data we need and the logger
        """
        self._username = username
        self._password = password
        self._host = host
        self._vhost = vhost
        self._services_exchange = services_exchange
        self._port = port
        self._routing_key = routing_key
        self._timeout = int(timeout)
        self._testrun_id = testrun_id

        # Zero out
        self._connection = None
        self._channel = None
        # Set signal handler
        signal.signal(signal.SIGALRM, self.close)
        # Set state
        self.state = DISCONNECTED
        #Timeout initialisation
        signal.signal(signal.SIGALRM, alarm_handler)

    #################################
    # PRIVATE METHODS
    #################################

    def _generate_queue_name(self):
        if (self._testrun_id):
            return "r" + str(self._testrun_id)
        else:
            return uuid.uuid1().hex

    def _declare(self):
        logger.debug("Declaring response queue: " + self._response_queue)
        self._channel.queue_declare(queue = self._response_queue, 
                                    durable = False, 
                                    exclusive = False,
                                    auto_delete=True)

        logger.debug('Declaring response exchange: '  + self._response_queue)
        self._channel.exchange_declare(exchange = self._response_queue, 
                                       type = 'direct',
                                       durable = False,
                                       auto_delete = True)

        logger.debug("Binding queue '%s' to exchange '%s' with routing key '%s'" % 
                     (self._response_queue, self._response_queue, self._response_queue))

        self._channel.queue_bind(queue = self._response_queue,
                                 exchange = self._response_queue,
                                 routing_key = self._response_queue)

    def _consume(self):
        """
        Tell amqplib we want to consume messages from the queue
        """
        logger.debug("Marked server as a consumer")
        self._channel.basic_consume(queue = self._response_queue, 
                                    callback = self._on_message,
                                    no_ack = True)

    def _on_message(self, message):
        """
        Handler for the messages
        """
        if self.state == WAITING_START:
            self._job_started()
        elif self.state == WAITING_END:
            self._job_finished()
        else:
            logger.error("Unknown message '%s' received" % ( message.body ))
        
    def _bulk_out_timeout(self):
        """
        Bulk out the timeout to allow cleaning up to happen on the worker
        Seperate method so it can be overridden in the test
        """
        return 10 + self._timeout
    
    def _job_started(self):
        """
        The job has been started - state transition 
        """
        logger.debug("job started with maximum of %s seconds to run" % ( self._timeout ))
        #Delay the timeout to give the worker chance to clear up
        #before the client starts consuming again
        timeout = self._bulk_out_timeout()
        self._trigger_timeout(timeout)
        self.state = WAITING_END
        #Now wait for the finished message
        self._channel.wait()
    
    def _job_finished(self):
        """
        The job has finished - state transition 
        """
        logger.debug('job finished')
        self.state = CONNECTED
        self._reset_timeout()
        self.close()

    ######################
    # Time out stuff
    ######################

    @staticmethod
    def _reset_timeout():
        """
        Reset the timeout 
        """
        logger.debug("Resetting client timeout")
        signal.alarm(0)

    @staticmethod
    def _trigger_timeout(seconds):
        """
        Start the timeout 
        """
        signal.alarm(seconds)

    def _start_wait_for_job_timeout(self):
        """
        Maximum wait for a worker to pick up the process       
        """
        five_hours = 5*60*60
        logger.info("Waiting for a worker to start the job with maximum time %s seconds"%(five_hours))
        self._trigger_timeout(five_hours)
        return five_hours
      
    ################

    def _start(self):
        """
        Start the job
        """
        ret_val = False
        start_timeout = self._start_wait_for_job_timeout()
        self.state = WAITING_START
        try:
            self._channel.wait()
            ret_val = True
        except Alarm:
            if self.state == WAITING_START:
                logger.debug("Timed out waiting for worker to take job")
                self.close()
                raise OtsWorkerStartTimeoutError(start_timeout)
            elif self.state == WAITING_END:
                logger.info("Timed out waiting for job to finish")
                self.close()
                raise OtsGlobalTimeoutError()
            else:
                logger.exception("Timeout in wrong state: " % (self.state))
                self.close()
                raise Exception()
        except Exception, e:
            logger.exception(e)
            raise e
        return ret_val
   
    def _send_message(self,message):
        """
        Sends a given thing to the client. Could be a string or a pickled object
        """
        try:
            logger.debug("Sending message '%s' to RabbitMQ" % ( message ))
            msg = amqp.Message(message)
            # Mark the message durable / persistent
            msg.properties['delivery_mode'] = 2
            self._trigger_timeout(10)
            self._channel.basic_publish(msg, 
                                        exchange = self._services_exchange,
                                        routing_key=self._routing_key)
            self._reset_timeout()
        except Exception, e:
            raise e

    def _does_queue_exist(self,queue):
        """
        Calls out to rabbitmqctl to check if a given queue exists
        """
        logger.debug("Checking if queue '%s' exists" % (queue))
        p = Popen('/usr/bin/sudo /usr/sbin/rabbitmqctl list_queues',
                  shell = True,
                  stdout = PIPE)
        output = p.communicate()[0]
        regex = re.compile('^%s\t' % (queue) )
        for line in output.splitlines():
            match = regex.match(line[:])
            if match:
                return True
        return False
            
    #############################################
    # PUBLIC METHODS
    #############################################

    def queue_name(self):
        return self._response_queue
    
    def run(self, commands, wait=True):
        """
        Runs a given command on the worker node
        """
        command = commands[0] #TODO
        success = False
        logger.debug("Preparing command '%s' for sending" % (command))

        if self._does_queue_exist(self._routing_key):

            self._response_queue = self._generate_queue_name()
            task_id = 1

            message = dict(command = [command],
                           response_queue = self._response_queue,
                           timeout = self._timeout,
                           task_id = task_id)

            self._declare()
            self._consume()
            #Pickle it and send it on it's way
            logger.debug("Sending message with command '%s'"%(command))
            self._send_message(dumps(message))
            #This is here to allow the tests to not wait for responses
            if wait:
                success = self._start()
                return success
        else:
            raise OtsQueueDoesNotExistError(self._routing_key)

    def connect(self):
        """
        Makes a connection the RabbitMQ server with the credentials that were
        supplied during construction. Streaming interface.
        """
        try:
            if self._connection is None:
                logger.debug("Connecting to RabbitMQ")
                self._trigger_timeout(10) # 10 seconds to connect
                self._connection = amqp.Connection(host = self._host, 
                                                   userid = self._username,
                                                   password = self._password,
                                                   virtual_host = self._vhost, 
                                                   insist = False)
                self._reset_timeout()
            else:
                logger.debug("Connection already present, not attempting to reconnect")
                
            if self._channel is None:
                self._trigger_timeout(10) # 10 seconds to fetch channel
                logger.debug("Opening channel")
                self._channel = self._connection.channel()
                self._reset_timeout()
            else:
                self._log.debug("Channel already present, not attempting to establish")
                
            self.state = CONNECTED
        except Exception, e:
            logger.exception(e)
            raise OtsConnectionError()

        # Streaming interface
        return self

        
    def close(self):
        try:
            logger.debug("Disconnecting from RabbitMQ")
            self._channel.close()
            self._connection.close()
            # Fix Memory leaks
            del self._channel.callbacks
            del self._connection.channels
            del self._connection.connection
            # Zero out
            self._channel = self._connection = None
            
            self._log.debug("Quitting")
            #Turn off the alarm handler
            self._reset_timeout()
            self.state = DISCONNECTED
        except:
            #Assume we weren't connected. Not a lot we can do here anyway
            pass

    def stop(self):
        self.close()

####################################

def _init_logging(config_filename):
    """
    Initialise the logging 
    """
    config = ConfigParser.ConfigParser()
    config.read(config_filename)
    try:
        log_filename = config.get("Client", "log_file", None)
    except ConfigParser.NoOptionError:
        log_filename = None
    
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    #Switch between file and STDERR based logging depending on config
    if log_filename is not None and os.path.exists(config_filename):
        log_handler = logging.FileHandler(log_filename,
                                          encoding="utf-8")
    else:
        log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

#####################################

def client_factory(device_name, timeout, config_file, testrun_id):
    """
    Instantiate a Client 
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    client = Client(username = config.get("Client", "username"),
                    password = config.get("Client", "password"),
                    host = config.get("Client", "host"),    
                    vhost = config.get("Client", "vhost"),
                    services_exchange = device_name,
                    port = config.getint("Client", "port"), 
                    routing_key = device_name,
                    testrun_id = testrun_id,
                    timeout = timeout)
    return client 

############################################

def main():
    """
    Entry point 
    """
    from optparse import OptionParser
    parser = OptionParser()
    #
    parser.add_option("-v", "--version",
                      action = "store_true",
                      help = "the version number of ots.distributor")    
    #
    parser.add_option("-d", "--device",
                      default = "foodevice",
                      help = "the device to be used")
    #
    parser.add_option("-t", "--timeout",
                      default = 30,
                      help = "the timeout")
    #
    cfg_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "config.ini")
    parser.add_option("-c", "--config",
                      default = cfg_filename,
                      help = "the config filename")
    #
    parser.add_option("-r", "--command",
                      default = "echo hello world",
                      help = "the command to run")
    #
    options, args = parser.parse_args()
    #
    if options.version:
        print "Version:", get_version()
        sys.exit(1)
    #
    if not os.path.exists(options.config):
        print "Config file path '%s' does not exist!" % ( options.config )
        sys.exit(1)
    _init_logging(options.config)

    testrun_id = ''
    client = client_factory(options.device, 
                            options.timeout, 
                            options.config, 
                            testrun_id)
    client.connect().run(options.command)


if __name__ == '__main__':
    main()
