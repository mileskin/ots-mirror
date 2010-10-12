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

import os
import time
import logging 
import ConfigParser
import unittest 
import zipfile
from stat import ST_CTIME
import multiprocessing
from socket import gethostname

from ots.common.testrun import Testrun


import ots.worker
import ots.worker.tests

import ots.server.distributor
from ots.server.distributor.taskrunner import RESULTS_SIGNAL, ERROR_SIGNAL
from ots.server.distributor.taskrunner import _testrun_queue_name
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.distributor.queue_exists import queue_exists
from ots.server.distributor.dev_utils.delete_queues import delete_queue
from ots.server.distributor.tests.system.worker_processes import WorkerProcesses


LOGGER = logging.getLogger(__name__)


DEBUG = False
HOST = "localhost"

TDF_TEMPLATE = """<?xml version="1.0" encoding="ISO-8859-1"?>
 <testdefinition version="1.0">
    <suite name="dummy suite" domain="Test">
        <description>description</description>
        <set name="dummy testset" feature="Test">
           <description>descripion</description>
              $CASES
        </set>
    </suite>
 </testdefinition>
"""

CASE_TEMPLATE = """
<case name="$NAME" type="Functional" level="Component">
    <step>$STEP</step>
</case>
"""


################################################

TEST_DEFINITION_XML = "test_definition.xml"
TEST_DEFINITION_ZIP = "test_definition.zip"

MODULE_DIRNAME = os.path.dirname(os.path.abspath(__file__))
TESTS_MODULE_DIRNAME = os.path.split(MODULE_DIRNAME)[0]



class TestDistribution(unittest.TestCase):

    def setUp(self):

        self.worker_processes = WorkerProcesses()

        config = ConfigParser.ConfigParser()
        config.read(self._worker_config_filename())
        self.queue = config.get('Worker','queue')
        #make sure there is no messages left in the worker queue 
        #from previous runs:
        #try:
        #    delete_queue("localhost", self.queue)
        #except:
        #    pass
        self.testrun = Testrun()
        self.testrun_id = None
          
    def tearDown(self):
        self.worker_processes.terminate()
        #self._remove_zip_file(TEST_DEFINITION_ZIP)
        self._remove_files_created_by_remote_commands()
        if self.queue:
            delete_queue("localhost", self.queue)
        if self.testrun_id:
            delete_queue("localhost", _testrun_queue_name(self.testrun_id))

    def _queue_exists(self, worker_config_filename):
        config = ConfigParser.ConfigParser()
        config.read(worker_config_filename)
        host = config.get('Worker','host')
        user_id = config.get('Worker','username')
        password = config.get('Worker','password')
        vhost = config.get('Worker','vhost')
        self.queue = config.get('Worker','queue')
        return queue_exists(host, user_id, password, vhost, self.queue)

    def _create_zip_test_definition_file(self, zip_filename, tdf_filename):
        zip_file_name = os.path.join(TESTS_MODULE_DIRNAME, 
                                     "data", zip_filename) 
        tdf_fqname = self._dummy_test_definition_xml_fqname(tdf_filename)
        file = zipfile.ZipFile(zip_file_name, "w")
        file.write(tdf_fqname, 
                   os.path.basename(tdf_fqname), 
                   zipfile.ZIP_DEFLATED)
        file.close()

    def _dynamic_create_zip_test_definition_file(self, zip_filename, steps):
        zip_filename = os.path.join(TESTS_MODULE_DIRNAME, 
                                 "data", zip_filename) 
        file = zipfile.ZipFile(zip_filename, "w")
        cases = ""
        for step in steps:
            case = CASE_TEMPLATE.replace("$NAME", step)
            case = case.replace("$STEP", step)
            cases += case
        tdf = TDF_TEMPLATE.replace("$CASES", cases)
        file.writestr(TEST_DEFINITION_XML, tdf)
        file.close()

    def _remove_zip_file(self, filename):
        zip_file_name = os.path.join(TESTS_MODULE_DIRNAME, "data", filename) 
        if os.path.exists(zip_file_name):
            os.unlink(zip_file_name)

    def _remove_files_created_by_remote_commands(self):
        foo = os.path.join(MODULE_DIRNAME, "foo") 
        if os.path.exists(foo):
            os.rmdir(foo)
        bar = os.path.join(MODULE_DIRNAME, "bar")
        if os.path.exists(bar):
            os.rmdir(bar)
        baz = os.path.join(MODULE_DIRNAME, "baz")
        if os.path.exists(baz):
            os.rmdir(baz)
        
    ###################
    # Tests
    ###################

    def test_one_task_one_worker(self):
        """
        Check that the results come back OK from the Worker 
        """
        self.worker_processes.start()
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        self._create_zip_test_definition_file(TEST_DEFINITION_ZIP, 
                                              TEST_DEFINITION_XML)              
        zipfile_name = os.path.join(TESTS_MODULE_DIRNAME,
                                    "data", 
                                    TEST_DEFINITION_ZIP)               
        command = ["ots_mock", '"%s"'%(zipfile_name), "%s" % self.testrun_id] 
        taskrunner.add_task(command)

        self.test_definition_file_received = False
        self.results_file_received = False

        def cb_handler(signal, **kwargs):
            self.cb_called = True
            result_object = kwargs['result']
            filename = result_object.name() 
            if filename == "test_definition.xml":
                self.test_definition_file_received = True
                expected = open(self._dummy_test_definition_xml_fqname(
                                   TEST_DEFINITION_XML), "r").read()
                self.assertEquals(expected, result_object.content)
            elif filename == "dummy_results_file.xml":
                self.results_file_received = True
                expected = self._dummy_results_xml(filename)
                self.assertEquals(expected, result_object.content)
            
        RESULTS_SIGNAL.connect(cb_handler) 
        
        time_before_run = time.time()
        time.sleep(1)
        taskrunner.run()
        time.sleep(1)
        time_after_run = time.time()

    
        if not DEBUG:
            foo = os.path.join(MODULE_DIRNAME, "foo") 
            foo_time = os.path.getctime(foo)
            bar = os.path.join(MODULE_DIRNAME, "bar")
            bar_time = os.path.getctime(bar)
            baz = os.path.join(MODULE_DIRNAME, "baz")
            baz_time = os.path.getctime(baz)


            self.assertTrue(time_before_run <
                            foo_time <= 
                            bar_time <= 
                            baz_time <=
                            time_after_run)

            self.assertTrue(self.results_file_received)
            self.assertTrue(self.test_definition_file_received)



    def test_two_tasks_one_worker(self):
        self.worker_processes.start()
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        #
        zipfile_1_name = os.path.join(TESTS_MODULE_DIRNAME,
                                    "data", 
                                    "test_definition_1.xml")
        steps = ["mkdir foo"]
        self._dynamic_create_zip_test_definition_file(zipfile_1_name,
                                                      steps)
        command_1 = ["ots_mock", '"%s"'%(zipfile_1_name), "%s" % self.testrun_id] 
        taskrunner.add_task(command_1)
        #
        zipfile_2_name = os.path.join(TESTS_MODULE_DIRNAME,
                                     "data", 
                                     "test_definition_2.xml")
        steps = ["mkdir bar"]               
        self._dynamic_create_zip_test_definition_file(zipfile_2_name,
                                                      steps)
        command_2 = ["ots_mock", '"%s"'%(zipfile_2_name), "%s" % self.testrun_id]
        taskrunner.add_task(command_2)

        
        time_before_run = time.time()
        time.sleep(1)
        taskrunner.run()
        time.sleep(1)
        time_after_run = time.time()

        if not DEBUG:
            foo = os.path.join(MODULE_DIRNAME, "foo") 
            foo_time = os.path.getctime(foo)
            bar = os.path.join(MODULE_DIRNAME, "bar")
            bar_time = os.path.getctime(bar)
            self.assertTrue(time_before_run < foo_time)
            self.assertTrue(foo_time <= bar_time)
            self.assertTrue(bar_time <= time_after_run)


    def test_two_tasks_two_worker(self):
        self.worker_processes.start(2)
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        #
        zipfile_1_name = os.path.join(TESTS_MODULE_DIRNAME,
                                    "data", 
                                    "test_definition_1.xml")
        steps = ["mkdir foo", "sleep 2"]
        self._dynamic_create_zip_test_definition_file(zipfile_1_name,
                                                      steps)
        command_1 = ["ots_mock", '"%s"'%(zipfile_1_name), "%s" % self.testrun_id] 
        taskrunner.add_task(command_1)
        #
        zipfile_2_name = os.path.join(TESTS_MODULE_DIRNAME,
                                     "data", 
                                     "test_definition_2.xml")
        steps = ["mkdir bar", "sleep 2"]               
        self._dynamic_create_zip_test_definition_file(zipfile_2_name,
                                                      steps)
        command_2 = ["ots_mock", '"%s"'%(zipfile_2_name), "%s" % self.testrun_id]
        taskrunner.add_task(command_2)

        time_before_run = time.time()
        time.sleep(1)
        taskrunner.run()
        time.sleep(1)
        time_after_run = time.time()

        if not DEBUG:
            foo = os.path.join(MODULE_DIRNAME, "foo") 
            foo_time = os.path.getctime(foo)
            bar = os.path.join(MODULE_DIRNAME, "bar")
            bar_time = os.path.getctime(bar)
            self.assertTrue(abs(foo_time - bar_time) < 0.1 ) 
            self.assertTrue(time_before_run <
                            foo_time <= 
                            bar_time <= 
                            time_after_run)

    #################################
    # HELPERS
    #################################

    @staticmethod
    def _worker_config_filename():
        module = os.path.dirname(os.path.abspath(ots.worker.__file__))
        worker_config_filename = os.path.join(module, "config.ini")
        if not os.path.exists(worker_config_filename):
            raise Exception("%s not found"%(worker_config_filename))
        return worker_config_filename

    @staticmethod
    def _distributor_config_filename():
        distributor_dirname = os.path.dirname(
                              os.path.abspath(ots.server.__file__))
        distributor_config_filename = os.path.join(distributor_dirname,
                                                  "config.ini")
        if not os.path.exists(distributor_config_filename):
            raise Exception("%s not found"%(distributor_config_filename))
        return distributor_config_filename

    @staticmethod
    def _distributor_config_file_for_test():
        distributor_dirname = os.path.dirname(
                              os.path.abspath(ots.server.distributor.__file__))
        distributor_config_filename = os.path.join(distributor_dirname, 
                                                  "tests", "system",
                                                  "test_config.ini")
        if not os.path.exists(distributor_config_filename):
            raise Exception("%s not found"%(distributor_config_filename))
        return distributor_config_filename

    @staticmethod
    def _dummy_results_xml(filename):
        dirname = os.path.dirname(os.path.abspath(ots.worker.tests.__file__))
        fqname = os.path.join(dirname, "data", filename)
        return open(fqname, "r").read()

    @staticmethod 
    def _dummy_test_definition_xml_fqname(filename):
        distributor_dirname = os.path.dirname(
                              os.path.abspath(ots.server.distributor.__file__))
        return os.path.join(distributor_dirname, "tests", 
                            "data", filename)



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
