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

and the ots_mock

Prerequisites:

 - RabbitMQ server running on localhost
"""


import os
import time
import unittest

from ots.common.testrun import Testrun

import ots.server
from ots.server.distributor.taskrunner import _testrun_queue_name
from ots.server.distributor.dev_utils.delete_queues import delete_queue
from ots.server.distributor.tests.system.worker_processes import WorkerProcesses
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.distributor.taskrunner import RESULTS_SIGNAL, ERROR_SIGNAL

class TestTimeouts(unittest.TestCase):

    def setUp(self):
        self.worker_processes = WorkerProcesses()
        self.queue = "foo"
        #make sure there is no messages left in the worker queue 
        #from previous runs:
        try:
            delete_queue("localhost", self.queue)
        except:
            pass
        self.testrun = Testrun()
        self.testrun_id = None
          
    def tearDown(self):
        self.worker_processes.terminate()
        if self.queue:
            delete_queue("localhost", self.queue)
        if self.testrun_id:
            delete_queue("localhost", _testrun_queue_name(self.testrun_id))

    def test_worker_side_timeout_single_task(self):
        """
        Check that worker timeout works properly.
        It should send error message about the timeout and
        "finished" state change

        """
        self.worker_processes.start()
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 1,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        command = ["sleep", "10"]

        taskrunner.add_task(command)
        self.cb_called = False
        def cb_handler(signal, **kwargs):
            self.cb_called = True
            self.assertEquals(kwargs['error_code'], "6001")
            self.assertTrue('Global timeout' in kwargs['error_info'])
            self.assertEquals(kwargs['sender'], 'TaskRunner')

        ERROR_SIGNAL.connect(cb_handler) 
        time_before_run = time.time()
        taskrunner.run()
        time_after_run = time.time()
        duration = time_after_run - time_before_run

        self.assertTrue(self.cb_called)
        self.assertTrue(duration < 6) # Should be less than 10 seconds


    def test_worker_side_timeout_multiple_tasks_multiple_workers(self):
        """
        Check that worker timeout works properly with multiple tasks.
        It should send error message about the timeout and
        "finished" state change

        """
        self.worker_processes.start(2)
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 1,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())

        command = ["sleep", "10"]

        taskrunner.add_task(command)
        taskrunner.add_task(command)
        self.cb_called = 0
        def cb_handler(signal, **kwargs):
            self.cb_called += 1
            self.assertEquals(kwargs['error_code'], "6001")
            self.assertTrue('Global timeout' in kwargs['error_info'])
            self.assertEquals(kwargs['sender'], 'TaskRunner')

        ERROR_SIGNAL.connect(cb_handler) 
        time_before_run = time.time()
        taskrunner.run()
        time_after_run = time.time()
        duration = time_after_run - time_before_run

        self.assertTrue(self.cb_called == 2)
        self.assertTrue(duration < 6) # Should be less than 10 seconds

    def test_worker_side_timeout_multiple_tasks_one_worker(self):
        """
        Check that worker timeout works properly with multiple tasks one worker.
        It should send error message about the timeout and
        "finished" state change

        """

        self.worker_processes.start()

        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 1,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        command = ["sleep", "10"]
        taskrunner.add_task(command)
        command = ["echo"]
        taskrunner.add_task(command)
        self.cb_called = 0
        def cb_handler(signal, **kwargs):
            self.cb_called += 1
            self.assertEquals(kwargs['error_code'], "6001")
            self.assertTrue('Global timeout' in kwargs['error_info'])
            self.assertEquals(kwargs['sender'], 'TaskRunner')

        ERROR_SIGNAL.connect(cb_handler) 
        time_before_run = time.time()
        taskrunner.run()
        time_after_run = time.time()
        duration = time_after_run - time_before_run

        self.assertEquals(self.cb_called, 1) # Only one of the commands fails
        self.assertTrue(duration < 6) # Should be less than 10 seconds

    @staticmethod
    def _distributor_config_filename():
        distributor_dirname = os.path.dirname(
                              os.path.abspath(ots.server.__file__))
        distributor_config_filename = os.path.join(distributor_dirname,
                                                  "config.ini")
        if not os.path.exists(distributor_config_filename):
            raise Exception("%s not found"%(distributor_config_filename))
        return distributor_config_filename


if __name__ == "__main__":
    unittest.main()

