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
Test the TaskRunner needs RabbitMQ to be running on localhost 
"""

import unittest 
import time

from pickle import dumps, loads

from amqplib import client_0_8 as amqp

from django.dispatch.dispatcher import Signal

from ots.server.distributor.task import Task
from ots.server.distributor.taskrunner import TaskRunner
from ots.server.distributor.taskrunner import _init_queue, TaskRunnerException
from ots.server.distributor.exceptions import OtsQueueDoesNotExistError, \
    OtsGlobalTimeoutError, OtsQueueTimeoutError, OtsConnectionError

from ots.common.protocol import OTSProtocol
from ots.common.protocol import get_version as get_ots_protocol_version
from ots.server.distributor.taskrunner import RESULTS_SIGNAL, ERROR_SIGNAL

class AMQPMessageStub:
    body = None

class TestTaskRunner(unittest.TestCase):

    def setUp(self):
        self.taskrunner = TaskRunner("guest", "guest", "localhost",
                                     "/", "ots", 5672, "test_taskrunner", 
                                     1, 60, 1)
        self.connection = amqp.Connection(host = "localhost", 
                                          userid = "guest",
                                          password = "guest",
                                          virtual_host = "/", 
                                          insist = False)
        self.channel = self.connection.channel()
        _init_queue(self.channel, 
                    "test_taskrunner", 
                    self.taskrunner._services_exchange,
                    "test_taskrunner")

    def tearDown(self):
        self.channel.queue_delete(queue = "test_taskrunner", nowait=True)

    def test_on_message_status(self):
        task_1 = Task([1, 2], 10)
        task_2 = Task([1, 2], 10)
     

        d = {OTSProtocol.MESSAGE_TYPE : OTSProtocol.STATE_CHANGE, 
             OTSProtocol.TASK_ID : task_1.task_id, 
             OTSProtocol.STATUS : OTSProtocol.STATE_TASK_STARTED,
             'version' : get_ots_protocol_version}
        message = AMQPMessageStub()
        message.body = dumps(d)

        self.taskrunner._tasks = [task_1, task_2] 
        self.taskrunner._on_message(message)
        self.assertEquals(2, len(self.taskrunner._tasks))

        d = {OTSProtocol.MESSAGE_TYPE : OTSProtocol.STATE_CHANGE, 
             OTSProtocol.TASK_ID : task_1.task_id, 
             OTSProtocol.STATUS : OTSProtocol.STATE_TASK_FINISHED,
             'version' : get_ots_protocol_version}
        message = AMQPMessageStub()
        message.body = dumps(d)
        
        self.taskrunner._on_message(message)
        self.assertEquals(1, len(self.taskrunner._tasks))
        self.assertEquals(task_2, self.taskrunner._tasks[0])

    def test_on_message_task(self):
        message = AMQPMessageStub()
        message.body = dumps({OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST,
                              'environment' : "foo",
                              'packages' : "bar",
                              'version' : get_ots_protocol_version})        
        def test_handler(signal, **kwargs):
            self.assertEquals(kwargs['environment'], 'foo')
            self.assertEquals(kwargs['packages'], 'bar')
        RESULTS_SIGNAL.connect(test_handler) 
        self.taskrunner._on_message(message)

    def test_on_message_error_message(self):
        message = AMQPMessageStub()
        message.body = dumps({OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTRUN_ERROR,
                              'error_info' : "foo",
                              'error_code' : 6,
                              'version' : get_ots_protocol_version})        
        def test_handler(signal, **kwargs):
            self.assertEquals(kwargs['error_info'], 'foo')
            self.assertEquals(kwargs['error_code'], 6)
        ERROR_SIGNAL.connect(test_handler)
        self.taskrunner._on_message(message)


    def test_dispatch_tasks(self):
        task_1 = Task([1, 2], 10)
        task_2 = Task([1, 2], 10)
        self.taskrunner._tasks = [task_1, task_2]
        self.taskrunner._dispatch_tasks()
        def test_cb(message):
            self.channel.basic_ack(delivery_tag = message.delivery_tag)
            self.assertEquals([1,2], loads(message.body)['command'])
        self.channel.basic_qos(0, 1, False)
        self.channel.basic_consume(queue = "test_taskrunner", 
                                   callback = test_cb)
        self.channel.wait()
        self.channel.wait()

    def test_wait_for_all_tasks(self):
        class ChannelStub:
            count = 5
            def __init__(self, taskrunner = None):
                self.taskrunner = taskrunner
            def wait(self):
                if self.taskrunner:
                    assert(range(self.count) == self.taskrunner._tasks)
                    self.taskrunner._tasks.pop()
                    self.count -= 1
        self.taskrunner._channel = ChannelStub()
        self.taskrunner._wait_for_all_tasks()
        self.taskrunner._tasks = [0,1,2,3,4]
        self.taskrunner._channel = ChannelStub(self.taskrunner)
        self.taskrunner._wait_for_all_tasks()

    def test_add_task(self):
        self.taskrunner.add_task([1,2,3])
        self.assertEquals(1, len(self.taskrunner._tasks))
        task = self.taskrunner._tasks[0]
        self.assertEquals([1,2,3], task.command)
        self.taskrunner._is_run = True
        self.assertRaises(TaskRunnerException, self.taskrunner.add_task, [1])


    def test_cannot_run_multiple_times(self):
        self.taskrunner._is_run = True
        self.assertRaises(TaskRunnerException, self.taskrunner.run)


class TestTimeoutScenarios(unittest.TestCase):


    def setUp(self):

#        import logging
#        logging.basicConfig(level=logging.DEBUG)
        self.connection = amqp.Connection(host = "localhost", 
                                          userid = "guest",
                                          password = "guest",
                                          virtual_host = "/", 
                                          insist = False)
        self.channel = self.connection.channel()

    def tearDown(self):
        # clear worker queue
        self.channel.queue_delete(queue = "test_taskrunner", nowait=True)

        # clear response queue
        self.channel.queue_delete(queue = "r1", nowait=True)

    def test_queue_timeout(self):

        taskrunner = TaskRunner("guest", "guest", "localhost",
                                "/", "ots", 5672, "test_taskrunner", 
                                1, 1, 1)

        _init_queue(self.channel, 
                    "test_taskrunner", 
                    taskrunner._services_exchange,
                    "test_taskrunner")


        taskrunner.add_task("dummycommand")
        self.assertRaises(OtsQueueTimeoutError, taskrunner.run)


    def test_server_side_global_timeout(self):

        # taskrunner with long enough queue timeout to get message processed
        # and very short global timeout to get hit after task started
        taskrunner = TaskRunner("guest", "guest", "localhost",
                                "/", "ots", 5672, "test_taskrunner", 
                                1, 1, 1)

        _init_queue(self.channel, 
                    "test_taskrunner", 
                    taskrunner._services_exchange,
                    "test_taskrunner")


        # Create a task
        task_1 = Task([1, 2], 10)
     
        # Create a "started" state change message

        taskrunner._tasks = [task_1] 
        self._publish_message(task_1.task_id, taskrunner._testrun_queue)
        self.assertRaises(OtsGlobalTimeoutError,
                          taskrunner.run)





    def _publish_message(self, task_id, response_queue):
#        import logging
        state = OTSProtocol.STATE_TASK_STARTED
        message = OTSProtocol.state_change_message(task_id, state)
        self.channel.basic_publish(message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)
#        logging.debug("published message to %s" % response_queue)



class TestQueueDoesnotExist(unittest.TestCase):

    def setUp(self):
        self.taskrunner = TaskRunner("guest", "guest", "localhost",
                                     "/", "ots", 5672, "NONEXISTING_QUEUE",
                                     1, 60, 1)
        self.connection = amqp.Connection(host = "localhost", 
                                          userid = "guest",
                                          password = "guest",
                                          virtual_host = "/", 
                                          insist = False)
        self.channel = self.connection.channel()
        _init_queue(self.channel, 
                    "test_taskrunner", 
                    self.taskrunner._services_exchange,
                    "test_taskrunner")

    def tearDown(self):
        self.channel.queue_delete(queue = "test_taskrunner", nowait=True)

    def test_queue_does_not_exist(self):
        self.assertRaises(OtsQueueDoesNotExistError, self.taskrunner.run)




class TestBackwardCompatibility(unittest.TestCase):
# some tests for the backward compatibility. To be removed after ots is deployed
# 


    def setUp(self):

#        import logging
#        logging.basicConfig(level=logging.DEBUG)
        self.connection = amqp.Connection(host = "localhost", 
                                          userid = "guest",
                                          password = "guest",
                                          virtual_host = "/", 
                                          insist = False)
        self.channel = self.connection.channel()

    def tearDown(self):
        # clear worker queue
        self.channel.queue_delete(queue = "test_taskrunner", nowait=True)

        # clear response queue
        self.channel.queue_delete(queue = "r1", nowait=True)


    def test_task_handling(self):
        taskrunner = TaskRunner("guest", "guest", "localhost",
                                "/", "ots", 5672, "test_taskrunner", 
                                1, 5, 5)

        _init_queue(self.channel, 
                    "test_taskrunner", 
                    taskrunner._services_exchange,
                    "test_taskrunner")


        self.error = False

        def test_handler(signal, **kwargs):
            self.error = True
        ERROR_SIGNAL.connect(test_handler) 


        # Create a task
        task_1 = Task(["echo", "jee"], 10)
     
        # Create a "started" and "finished" state change messages

        taskrunner._tasks = [task_1] 
        self._publish_message(taskrunner._testrun_queue,
                              OTSProtocol.STATE_TASK_STARTED)

        taskrunner._tasks = [task_1] 
        self._publish_message(taskrunner._testrun_queue,
                              OTSProtocol.STATE_TASK_FINISHED)


        taskrunner.run()
        self.assertTrue(task_1.is_finished)
        self.assertFalse(self.error)


    def test_global_timeout(self):
        global_timeout = 2
        queue_timeout = 10
        taskrunner = TaskRunner("guest", "guest", "localhost",
                                "/", "ots", 5672, "test_taskrunner", 
                                1, global_timeout, queue_timeout)

        _init_queue(self.channel, 
                    "test_taskrunner", 
                    taskrunner._services_exchange,
                    "test_taskrunner")


        self.error = False

        def test_handler(signal, **kwargs):
            self.error = True
        ERROR_SIGNAL.connect(test_handler) 


        # Create a task
        task_1 = Task(["echo", "jee"], global_timeout)
        taskrunner._tasks = [task_1] 
     
        # Create a "started" message to trigger global timeout
        self._publish_message(taskrunner._testrun_queue,
                              OTSProtocol.STATE_TASK_STARTED)

        time_before_run = time.time()
        self.assertRaises(OtsGlobalTimeoutError, taskrunner.run)
        time_after_run = time.time()
        duration = time_after_run - time_before_run
        
        # In backward compatibility mode timeout is global timeout and not
        # global_timeout + queue_timeout
        self.assertTrue(duration < global_timeout+queue_timeout)

    def _publish_message(self, response_queue, state):

        message = amqp.Message(dumps(state))

        self.channel.basic_publish(message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)


if __name__ == "__main__":
    unittest.main()
