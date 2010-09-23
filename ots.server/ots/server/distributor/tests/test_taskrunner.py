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

from ots.common.dto.api import StateChangeMessage, TaskCondition

from ots.server.distributor.task import Task
from ots.server.distributor.taskrunner import TaskRunner
from ots.server.distributor.taskrunner import _init_queue, TaskRunnerException
from ots.server.distributor.exceptions import OtsQueueDoesNotExistError, \
    OtsGlobalTimeoutError, OtsQueueTimeoutError, OtsConnectionError
from ots.server.distributor.taskrunner import TASKRUNNER_SIGNAL

class AMQPMessageStub:
    body = None

class Foo(object):
    bar = 1
        
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
        
        start_msg = StateChangeMessage(task_1.task_id,
                                       TaskCondition.START)
        message = AMQPMessageStub()
        message.body = dumps(start_msg)

        self.taskrunner._tasks = [task_1, task_2] 
        self.taskrunner._on_message(message)
        self.assertEquals(2, len(self.taskrunner._tasks))

        
        end_msg = StateChangeMessage(task_1.task_id,
                                       TaskCondition.FINISH)
        message = AMQPMessageStub()
        message.body = dumps(end_msg)
        
        self.taskrunner._on_message(message)
        self.assertEquals(1, len(self.taskrunner._tasks))
        self.assertEquals(task_2, self.taskrunner._tasks[0])

    def test_on_message_relay(self):
        message = AMQPMessageStub()
        message.body = dumps(Foo())        
        def test_handler(signal, datatype, **kwargs):
            self.assertTrue(isinstance(datatype, Foo))
            self.assertEquals(1, datatype.bar)
        TASKRUNNER_SIGNAL.connect(test_handler) 
        self.taskrunner._on_message(message)

    def test_dispatch_tasks(self):
        task_1 = Task(["1", "2"], 10)
        task_2 = Task(["1", "2"], 10)
        self.taskrunner._tasks = [task_1, task_2]
        self.taskrunner._dispatch_tasks()
        def test_cb(message):
            self.channel.basic_ack(delivery_tag = message.delivery_tag)
            self.assertEquals("1 2", loads(message.body).command)
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


    #FIXME Broken Test
    def _test_queue_timeout(self):

        taskrunner = TaskRunner("guest", "guest", "localhost",
                                "/", "ots", 5672, "test_taskrunner", 
                                1, 1, 1)

        _init_queue(self.channel, 
                    "test_taskrunner", 
                    taskrunner._services_exchange,
                    "test_taskrunner")


        taskrunner.add_task("dummycommand")
        self.assertRaises(OtsQueueTimeoutError, taskrunner.run)


    #FIXME Broken Test
    def _test_server_side_global_timeout(self):

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
        task_1 = Task(["1", "2"], 10)
     
        # Create a "started" state change message

        taskrunner._tasks = [task_1] 
        self._publish_message(task_1.task_id, taskrunner._testrun_queue)
        self.assertRaises(OtsGlobalTimeoutError,
                          taskrunner.run)

    def _publish_message(self, task_id, response_queue):
        start_msg = StateChangeMessage(task_id, TaskCondition.START)
        message = pack_message(start_msg)
        self.channel.basic_publish(message,
                                   mandatory = True,
                                   exchange = response_queue,
                                   routing_key = response_queue)




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




if __name__ == "__main__":
    unittest.main()
