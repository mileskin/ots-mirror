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
from ots.common.dto.api import DTO_SIGNAL
from ots.common.amqp.api import run_queue_name 
from ots.common.amqp.api import pack_message

import ots.worker
import ots.worker.tests

import ots.server.distributor
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.server_config_filename import server_config_filename

from ots.tools.queue_management.delete_queue import delete_queue
from ots.server.distributor.tests.component.worker_processes \
                                      import WorkerProcesses

#Debug to allow running of Worker in separate terminal
DEBUG = False

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
          
    def tearDown(self):
        if not DEBUG:
            self.worker_processes.terminate()
        if self.queue:
            delete_queue("localhost", self.queue)
        if self.testrun_id:
            delete_queue("localhost", run_queue_name(self.testrun_id))

    def test_failing_task(self):
        if not DEBUG:
            self.worker_processes.start()
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             routing_key = ROUTING_KEY, 
                             execution_timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = server_config_filename())
        
        command = ["command_error_mock", "localhost", str(self.testrun_id)] 
        taskrunner.add_task(command)
        
        self.is_exception_raised = False

        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, Exception):
                print "cb_handler  Exception"
                self.is_exception_raised = True
                #Replicate case for Taskrunner is in a process 
                #the proc stops when Exception is raised by closing tr
                taskrunner._close()

        DTO_SIGNAL.connect(cb_handler)       

        #
        try:
            taskrunner.timeout_handler.stop()
            taskrunner.run()
        except AttributeError:
            pass
        
        self.assertTrue(self.is_exception_raised)

        #Worker reconnect hiatus
        time.sleep(5)
        #
        self.send_quit()
        
        #Worker shut down hiatus
        time.sleep(2)
        if not DEBUG:
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

        channel.basic_publish(message, 
                              exchange = ROUTING_KEY,
                              routing_key = ROUTING_KEY)

                 
if __name__ == "__main__": 
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
