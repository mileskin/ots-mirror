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

from ots.common.testrun import Testrun

import ots.worker
import ots.worker.tests

import ots.server.distributor
from ots.server.distributor.taskrunner import RESULTS_SIGNAL
from ots.server.distributor.taskrunner import _testrun_queue_name
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.distributor.dev_utils.delete_queues import delete_queue
from ots.server.distributor.tests.system.worker_processes import WorkerProcesses

DEVICE_GROUP = "food" 

class TestPropertiesDistribution(unittest.TestCase):

    def setUp(self):
        self.queue = DEVICE_GROUP

        #make sure there is no messages left in the worker queue 
        #from previous runs:
        try:
            delete_queue("localhost", self.queue)
        except:
            pass
        #
        self.worker_processes = WorkerProcesses()

        self.testrun = Testrun()
        self.testrun_id = None
          
    def tearDown(self):
        self.worker_processes.terminate()
        if self.queue:
            delete_queue("localhost", self.queue)
        if self.testrun_id:
            delete_queue("localhost", _testrun_queue_name(self.testrun_id))

    #############################
    # Test Single Property
    #############################

    def test_property_0(self):
        """
        Test (None, None, "property")
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        self.worker_processes.start(routing_key = "food.#")

        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = DEVICE_GROUP, 
                             timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename(),
                             routing_key = "food.pie")
       
        taskrunner.add_task(["echo","foo"])
        taskrunner.run()

    def _test_property_1(self):
        """
        Test for (None, "property", None)
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        pass

    def _test_property_2(self):
        """
        Test for (None, "property", None)
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        pass

    #############################
    # Test Multiple Propertys
    #############################

    def _test_property_1_0(self):
        """
        Test (None, "property_1", "property_0")
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        pass

    def _test_property_2_1(self):
        """
        Test ("property_2", "property_1", None)
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        pass

    def _test_property_3_2_1(self):
        """
        Test ("property_2", "property_1", "property_0")
        """
        #Check arrived at correct worker
        #Check one and only one worker takes the task
        pass

    ###############################
    # HELPERS
    ###############################

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
