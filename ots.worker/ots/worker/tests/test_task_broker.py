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

import logging
import unittest 
import subprocess
import time
from pickle import dumps

from amqplib import client_0_8 as amqp
from amqplib.client_0_8.exceptions import AMQPChannelException

from ots.worker.connection import Connection
from ots.worker.task_broker import TaskBroker
from ots.common.protocol import OTSProtocol, OTSMessageIO
from ots.common.protocol import get_version as get_ots_protocol_version
from ots.worker.command import SoftTimeoutException
from ots.worker.command import HardTimeoutException
from ots.worker.command import CommandFailed


##########################################
# Utility Functions
##########################################

def _init_queue(channel, queue, exchange, routing_key):
    """
    Initialise a durable queue and a direct exchange
    with a routing_key of the name of the queue

    @type channel: C{amqplib.client_0_8.channel.Channel}  
    @param channel: The AMQP channel

    @rtype queue: C{string}  
    @return queue: The queue name
    """
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



def _queue_size(queue):
    """
    Get the size of the queue 
    
    rtype: C{int} or None if there is no queue
    rparam:  Queue Size
    """
    ret_val = None
    connection = amqp.Connection(host = "localhost",
                                 userid = "guest",
                                 password = "guest",
                                 virtual_host = "/",
                                 insist = False)
    channel = connection.channel()
    try:
        name, msg_count, consumers = channel.queue_declare(queue = queue, 
                                                  passive = True)
        ret_val = msg_count
    except AMQPChannelException:
        pass
    return ret_val 


###########################################
# TestTaskBroker
###########################################

class TestTaskBroker(unittest.TestCase):

    def tearDown(self):

        # A quick and dirty way to make sure "test" queue gets cleaned
        task_broker = self.create_task_broker()

        channel = task_broker.channel
        channel.queue_delete(queue = "test", nowait = True)

    def create_task_broker(self, dispatch_func=None):
        connection = Connection(vhost = "/",
                                host = "localhost",
                                port = 5672,
                                username = "guest",
                                password = "guest")
        connection.connect()
        task_broker = TaskBroker(connection, "test", "test", "test")
        if dispatch_func:
            task_broker._dispatch = dispatch_func
        task_broker._init_connection()
        return task_broker

    def create_message(self, command, timeout, response_queue, task_id,
                             min_worker_version = 0.05):
         return {OTSProtocol.MIN_WORKER_VERSION : min_worker_version, 
                 OTSProtocol.COMMAND : [command],
                 OTSProtocol.TIMEOUT : timeout,
                 OTSProtocol.RESPONSE_QUEUE : response_queue,
                 OTSProtocol.TASK_ID : task_id,
                 OTSProtocol.VERSION : get_ots_protocol_version()}


    def test_consume(self):
        """
        Check that the consume sets the prefetch correctly 
        """
        def check_queue_size(*args,**kwargs):
            """
            Closure to attach to _dispatch 
            to check the queue size
            """
            self.assertEquals(self.expected_size, _queue_size("test"))
        self.assertTrue(_queue_size("test") is None)
        
        #SetUp the TaskBroker but override _dispatch
        task_broker = self.create_task_broker(dispatch_func=check_queue_size)

        #Publish a Couple of Messages
        channel = task_broker.channel
        foo_msg = amqp.Message(dumps(self.create_message('foo', 1, '', 1)))
        channel.basic_publish(foo_msg,
                              mandatory = True,
                              exchange = "test",
                              routing_key = "test")

        bar_msg = amqp.Message(dumps(self.create_message('bar', 1, '', 1)))
        channel.basic_publish(bar_msg,
                              mandatory = True,
                              exchange = "test",
                              routing_key = "test")
       
        self.assertEquals(2, _queue_size("test"))
        task_broker._consume()
        self.expected_size = 1
        channel.wait()
        self.expected_size = 0
        channel.wait()
       

    def test_init_connection(self):
        #use test durable code here
        pass

    def _test_loop(self):
        class ConnectionStub:
            exits = False
            def clean_up(self):
                self.exits = True
        connection_stub = ConnectionStub()
        task_broker = TaskBroker(connection_stub, None, None, None)
        
        #Case where no stop file and keep_looping_true
        class ChannelStub:
            wait_called = False
            def wait(self): 
                self.wait_called = True
                task_broker._keep_looping = False
        channel_stub = ChannelStub()
        task_broker._connection.channel = channel_stub
        task_broker._loop()
        self.assertTrue(channel_stub.wait_called)

        #Case where keep_looping False
        task_broker._keep_looping = False
        task_broker._loop()
        self.assertTrue(connection_stub.exits)

        #Case where stop_file_exists
        connection_stub.exits = False
        task_broker._keep_looping = True
        def _stop_file_exists():
            return True
        task_broker._stop_file_exists = _stop_file_exists
        task_broker._loop()
        self.assertTrue(connection_stub.exits)

    def test_on_message(self):
        logging.basicConfig()
        #send a sleep command
        #send an echo command
        #watch the response queue for state changes
        #check the foo queue to see that echo remains on the queue
        msg1 = self.create_message('sleep 1', 2, 'test', 1)
        msg2 = self.create_message('echo "bogus message"', 1, 'test', 1)
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        # Send some commands
        for message in [msg1, msg2]:
            channel.basic_publish(amqp.Message(dumps(message)),
                                  mandatory = True,
                                  exchange = "test",
                                  routing_key = "test")

        #Set to Consume
        task_broker._consume()
        channel.wait()
        time.sleep(1)
        channel.wait()
        time.sleep(1)
	# We should have our command + state change messages in the queue
        self.assertEquals(_queue_size("test"), 3)


    def test_on_message_timeout(self):
        import logging
        logging.basicConfig()
        #send a sleep command
        msg1 = self.create_message('sleep 2', 1, 'test', 1)

        task_broker = self.create_task_broker()
        channel = task_broker.channel
        # Send timeouting command

        channel.basic_publish(amqp.Message(dumps(msg1)),
                              mandatory = True,
                              exchange = "test",
                              routing_key = "test")

        #Set to Consume
        task_broker._consume()
        channel.wait()
        time.sleep(3)
	# We should have state change messages + timeout msg
        self.assertEquals(2, _queue_size("test"))


    def test_dispatch(self):
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        # Try to keep under timeouts
        self.assertFalse(task_broker._dispatch(OTSProtocol.COMMAND_IGNORE, 1))
        self.assertFalse(task_broker._dispatch(OTSProtocol.COMMAND_QUIT, 1))
        self.assertFalse(task_broker._dispatch("ls -al", 1))

    def test_dispatch_timeout(self):
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        # Try to keep under timeouts
        self.assertRaises(SoftTimeoutException, task_broker._dispatch, "sleep 2", 1)

    def test_dispatch_failing_command(self):
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        # Try to keep under timeouts
        self.assertRaises(CommandFailed,
                          task_broker._dispatch,
                          "cat /not/existing/file",
                          1)


    def test_publish_task_state_change(self):
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        task_id = 1
        response_queue = 'test'
        self.assertEquals(0, _queue_size(response_queue))
        task_broker._publish_task_state_change(task_id, response_queue)
        self.assertEquals(1, _queue_size(response_queue))

    def test_publish_error_message(self):
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        task_id = 1
        response_queue = 'test'

        error_info = "task 1 timed out"
        error_code = 666
        self.assertEquals(0, _queue_size(response_queue))
        task_broker._publish_error_message(task_id,
                                           response_queue,
                                           error_info,
                                           error_code)
        self.assertEquals(1, _queue_size(response_queue))

    def test_stop_file_exists(self):
        task_broker = self.create_task_broker()
        self.assertFalse(task_broker._stop_file_exists())    

    def test_is_version_compatible(self):
        task_broker = self.create_task_broker()
        packed_msg = OTSMessageIO.pack_command_message(["ls"], "foo", 2, 111,
                                                       min_worker_version = 100)
        self.assertFalse(task_broker._is_version_compatible(packed_msg))

        packed_msg = OTSMessageIO.pack_command_message(["ls"], "foo", 2, 111,
                                                       min_worker_version = 0.7)
        self.assertTrue(task_broker._is_version_compatible(packed_msg))

    def test_on_message_not_version_compatible(self):
        """
        Check that incompatible versions dont
        pull messages from the queue
        """
        self.assertTrue(_queue_size("test") is None)
        logging.basicConfig()
        msg1 = self.create_message('echo foo', 1, 'test', 1,
                                   min_worker_version = 10)
        task_broker = self.create_task_broker()
        channel = task_broker.channel
        channel.basic_publish(amqp.Message(dumps(msg1)),
                              mandatory = True,
                              exchange = "test",
                              routing_key = "test")
        self.assertEquals(1, _queue_size("test"))
        task_broker._consume()
        channel.wait()
        self.assertEquals(1, _queue_size("test"))

        #Check that the message can be pulled by another consumer
        connection = amqp.Connection(host = "localhost", 
                                          userid = "guest",
                                          password = "guest",
                                          virtual_host = "/", 
                                          insist = False)
        channel = connection.channel()
        _init_queue(channel, 
                    "test", 
                    "test",
                    "test")
        self.received = False
        def cb(message):
            channel.basic_ack(delivery_tag = message.delivery_tag)
            self.received = True
        channel.basic_consume("test", callback = cb)
        channel.wait()
        self.assertTrue(self.received)
        self.assertEquals(0, _queue_size("test"))

if __name__ == "__main__":
    unittest.main()
