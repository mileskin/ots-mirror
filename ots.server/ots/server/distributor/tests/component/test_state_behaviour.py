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
Component Test for OTS-Core 

Runs an Integration Test on Components:

    - ots.server.distributor
    - ots.worker
    - ots.common

and the command_error_mock

Prerequisites:

 - RabbitMQ server running on localhost
"""

################################################

import os
import unittest 
import time

from amqplib import client_0_8 as amqp

from ots.common.dto.api import CommandMessage
from ots.server.distributor.api import DTO_SIGNAL
from ots.common.amqp.api import testrun_queue_name
from ots.common.amqp.api import pack_message

import ots.worker
import ots.worker.tests

import ots.server.distributor
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.server_config_filename import server_config_filename
from ots.server.distributor.exceptions import OtsExecutionTimeoutError
from ots.tools.queue_management.delete_queue import delete_queue
from ots.server.distributor.tests.component.worker_processes \
                                      import WorkerProcesses

#Debug to allow running of Worker in separate terminal
DEBUG = False
VERBOSE = False

ROUTING_KEY = "foo"

class TestStateBehaviour(unittest.TestCase):

    def setUp(self):
        self.queue = ROUTING_KEY
        try:
            if not DEBUG:
                delete_queue("localhost", self.queue)
        except:
            pass
        #
        if not DEBUG:
            self.worker_processes = WorkerProcesses()
            self.testrun_id = None
            self.testrun_id2 = None
          
    def tearDown(self):
        if not DEBUG:
            self.worker_processes.terminate()
        if self.queue:
            delete_queue("localhost", self.queue)
        if self.testrun_id:
            delete_queue("localhost", testrun_queue_name(self.testrun_id))
        if self.testrun_id2:
            delete_queue("localhost", testrun_queue_name(self.testrun_id2))

    def test_failing_task(self):
        if not DEBUG:
            self.worker_processes.start()
        self.testrun_id = 111
        taskrunner = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = _distributor_config_filename())

        command = ["command_error_mock", "localhost", str(self.testrun_id)]
        taskrunner.add_task(command)
        
        self.is_exception_raised = False

        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, Exception):
                self.is_exception_raised = True

        DTO_SIGNAL.connect(cb_handler)
        
        taskrunner.run()
        
        self.assertTrue(self.is_exception_raised)
        self.send_quit()
        time.sleep(1)

        self.assertFalse(all(self.worker_processes.exitcodes))

    def test_worker_alive_after_failing_task(self):
        if not DEBUG:
            self.worker_processes.start()
        self.testrun_id = 111
        taskrunner1 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = _distributor_config_filename())

        command = ["command_error_mock", "localhost", str(self.testrun_id)]
        taskrunner1.add_task(command)
        
        self.is_exception_raised = False

        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, Exception):
                self.is_exception_raised = True

        DTO_SIGNAL.connect(cb_handler)
        
        taskrunner1.run()
        
        self.assertTrue(self.is_exception_raised)
        
        self.is_exception_raised = False

        # Trigger another task to make sure worker is still alive
        taskrunner2 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = _distributor_config_filename())

        command = ["echo", "foo"]
        taskrunner2.add_task(command)
        taskrunner2.run()
        self.assertFalse(self.is_exception_raised)

        self.send_quit()
        time.sleep(1)

        self.assertFalse(all(self.worker_processes.exitcodes))

    def test_worker_alive_after_server_timeout(self):
        if not DEBUG:
            self.worker_processes.start()
        self.testrun_id = 111
        self.testrun_id2 = 112
        taskrunner1 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = _distributor_config_filename())

        command = ["sleep", "5"]
        taskrunner1.add_task(command)

        self.is_exception_raised = False

        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, Exception):
                self.is_exception_raised = True

        DTO_SIGNAL.connect(cb_handler)

        # Overwrite server side timeout handler with a one that timeouts
        from ots.server.distributor.timeout import Timeout
        taskrunner1.timeout_handler = Timeout(1,
                                       1,
                                       1)

        self.assertRaises(OtsExecutionTimeoutError, taskrunner1.run)
        
#        self.assertTrue(self.is_exception_raised)
        
        self.is_exception_raised = False

        time.sleep(10) # Give worker time to reconnect

    # Trigger another task to make sure worker is still alive
        taskrunner2 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id2,
                             config_file = _distributor_config_filename())
        taskrunner2.add_task(["echo", "foo"])
        taskrunner2.run()
        self.assertFalse(self.is_exception_raised)

        self.send_quit()
        time.sleep(1)

        self.assertFalse(all(self.worker_processes.exitcodes))

    def test_worker_alive_after_server_timeout_failing_task(self):
        if not DEBUG:
            self.worker_processes.start()
        self.testrun_id = 111
        self.testrun_id2 = 112
        taskrunner1 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = _distributor_config_filename())

        command = ["sleep", "5",";",
                   "command_error_mock", "localhost", str(self.testrun_id)]
        taskrunner1.add_task(command)

        self.is_exception_raised = False

        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, Exception):
                self.is_exception_raised = True

        DTO_SIGNAL.connect(cb_handler)

        # Overwrite server side timeout handler with a one that timeouts
        from ots.server.distributor.timeout import Timeout
        taskrunner1.timeout_handler = Timeout(1,
                                       1,
                                       1)

        self.assertRaises(OtsExecutionTimeoutError, taskrunner1.run)
        
#        self.assertTrue(self.is_exception_raised)
        
        self.is_exception_raised = False

        time.sleep(10) # Give worker time to reconnect


    # Trigger another task to make sure worker is still alive
        taskrunner2 = taskrunner_factory(
                             routing_key = ROUTING_KEY,
                             execution_timeout = 10,
                             testrun_id = self.testrun_id2,
                             config_file = _distributor_config_filename())
        taskrunner2.add_task(["echo", "foo"])
        taskrunner2.run()
        self.assertFalse(self.is_exception_raised)

        self.send_quit()
        time.sleep(1)

        self.assertFalse(all(self.worker_processes.exitcodes))


    def send_quit(self):
        cmd_msg = CommandMessage(["quit"],
                                 self.queue,
                                 111)
        message = pack_message(cmd_msg)

        conn = amqp.Connection(host = "localhost", 
                        userid = "guest",
                        password = "guest",
                        virtual_host = "/", 
                        insist = False)
        channel = conn.channel()
        channel.basic_publish(message, 
                              exchange = ROUTING_KEY,
                              routing_key = ROUTING_KEY)

        
def _distributor_config_filename():
    distributor_dirname = os.path.dirname(
        os.path.abspath(__file__))
    distributor_config_filename = os.path.join(distributor_dirname,
                                               "test_config.ini")
    if not os.path.exists(distributor_config_filename):
        raise Exception("%s not found"%(distributor_config_filename))
    return distributor_config_filename


                 
if __name__ == "__main__": 
    if VERBOSE:
        import logging
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(log_handler)
    unittest.main()
