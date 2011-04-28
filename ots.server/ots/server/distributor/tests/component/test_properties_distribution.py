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

and the ots_mock

Prerequisites:

 - RabbitMQ server running on localhost
"""

################################################


# A Starting point for the introduction 
# of more complex "addressing" of Tasks
#
# Currently three orthogonal 'property' levels
# property_2 , property_1 , property_0

import unittest


import os
import time
import unittest 
import zipfile

from ots.server.distributor.api import DTO_SIGNAL
from ots.common.amqp.api import testrun_queue_name 

from ots.tools.queue_management.delete_queue import delete_queue

import ots.worker
import ots.worker.tests

import ots.server.distributor
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.distributor.tests.component.worker_processes \
                                                   import WorkerProcesses
from ots.server.distributor.exceptions import OtsQueueDoesNotExistError
from ots.server.distributor.exceptions import OtsQueueTimeoutError

# all used queues based on worker config files under data/
ALL_QUEUES = [
    "group1",
    "group1.device1",
    "group1.device1.hwid1",
    "group1.device1.hwid2",
    "group1.device2",
    "group1.device2.hwid1",
    "group2",
    "group2.device1",
    "group2.device1.hwid1",
    ]

def _config_path(file):
    "returns the absolute path to the config file under data/ directory"
    module = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module,"data", file)

class TestPropertiesDistribution(unittest.TestCase):

    def cleanup(self):
        try:
            for queue in ALL_QUEUES:
                delete_queue("localhost", queue)
                os.system("rm -f /tmp/%s" %queue)
        except:
            pass
        
    def run_task(self, routing_key):
        """
        sends 'echo $PPID >> /tmp/routing_key' command to the routing_key and makes sure it is executed
        by checking that the file exists. Returns the $PPID value read from the file
        """
        self.assertFalse(os.path.isfile("/tmp/%s" % routing_key))
        taskrunner1 = taskrunner_factory(
                             routing_key = routing_key, 
                             execution_timeout = 2,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
       
        taskrunner1.add_task(["echo", "$PPID",">>","/tmp/%s" % routing_key])
        taskrunner1.run()
        self.assertTrue(os.path.isfile("/tmp/%s" % routing_key))
        f = open('/tmp/%s'% routing_key, 'r')
        read_data = f.read()
        f.close()
        os.system("rm -f /tmp/%s" % routing_key)
        return read_data

    def setUp(self):
        #make sure there is no messages left in the worker queue 
        #from previous runs:
        self.cleanup()
        #
        self.worker_processes = WorkerProcesses()
        self.testrun_id = None
          
    def tearDown(self):
        self.worker_processes.terminate()
        self.cleanup()
        if self.testrun_id:
            delete_queue("localhost", testrun_queue_name(self.testrun_id))

    def test_worker_consumes_from_all_queues(self):
        # Starts 1 worker with group1, device1, hwid1
        # Checks that worker consumes from all queues
        #
        self.worker_processes.start(1, _config_path("group1_device1_hwid1.ini"))

        self.testrun_id = 111      
        
        self.run_task("group1")
        self.run_task("group1.device1")
        self.run_task("group1.device1.hwid1")

    def test_worker_consumes_only_from_right_queues(self):
        # Starts 1 worker with group1, device1, hwid1
        # Checks that worker consumes only from right queues
        #

        # Start another worker to make sure "false" queues exist
        worker1 = self.worker_processes.start(1, _config_path("group1_device1_hwid1.ini"))


        # Start the actual worker we want to test
        worker2 = self.worker_processes.start(1, _config_path("group1.ini"))
        

        self.testrun_id = 111

        # This can go to one of the workers
        task_pid = int(self.run_task("group1"))
        self.assertTrue(task_pid == worker1[0] or task_pid == worker2[0])

        # These should go to worker1
        task_pid = int(self.run_task("group1.device1"))
        self.assertEquals(task_pid, worker1[0])

        task_pid = int(self.run_task("group1.device1.hwid1"))
        self.assertEquals(task_pid, worker1[0])

        # Make sure workers don't follow wrong queues does not get executed
        self.assertRaises(OtsQueueDoesNotExistError, self.run_task, "group2")
        self.assertRaises(OtsQueueDoesNotExistError, self.run_task, "group1.device2")
        self.assertRaises(OtsQueueDoesNotExistError, self.run_task, "group1.device1.hwid2")
        self.assertRaises(OtsQueueDoesNotExistError, self.run_task, "group1.device2.hwid1")



    def test_workers_consume_only_from_right_queues_with_multiple_workers(self):

        worker1 = self.worker_processes.start(1, _config_path("group1_device1_hwid1.ini"))
        worker2 = self.worker_processes.start(1, _config_path("group1_device1_hwid2.ini"))
        worker3 = self.worker_processes.start(1, _config_path("group1_device2_hwid1.ini"))
        worker4 = self.worker_processes.start(1, _config_path("group1.ini"))
        worker5 = self.worker_processes.start(1, _config_path("group2_device1_hwid1.ini"))

        time.sleep(2)


        self.testrun_id = 111

        # This can go to workers 1,2,3,4
        expected_pids = (worker1[0], worker2[0], worker3[0], worker4[0])
        task_pid = int(self.run_task("group1"))
        self.assertTrue(task_pid in expected_pids)

        # This should go to worker1
        task_pid = int(self.run_task("group1.device1.hwid1"))
        self.assertEquals(task_pid, worker1[0])

        # This should go to worker2
        task_pid = int(self.run_task("group1.device1.hwid2"))
        self.assertEquals(task_pid, worker2[0])

        # This should go to worker3
        task_pid = int(self.run_task("group1.device2"))
        self.assertEquals(task_pid, worker3[0])

        # This should go to worker3
        task_pid = int(self.run_task("group1.device2.hwid1"))
        self.assertEquals(task_pid, worker3[0])

        # This should go to worker5
        task_pid = int(self.run_task("group2"))
        self.assertEquals(task_pid, worker5[0])


    ###############################
    # HELPERS
    ###############################

    @staticmethod
    def _distributor_config_filename():
        distributor_dirname = os.path.dirname(
                              os.path.abspath(__file__))
        distributor_config_filename = os.path.join(distributor_dirname,
                                                  "test_config.ini")
        if not os.path.exists(distributor_config_filename):
            raise Exception("%s not found"%(distributor_config_filename))
        return distributor_config_filename


if __name__ == "__main__":
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.ERROR)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    unittest.main()
