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
from logging import LogRecord
import ConfigParser
import unittest 
import zipfile
from stat import ST_CTIME
import multiprocessing
from socket import gethostname

from ots.common.dto.api import DTO_SIGNAL
from ots.common.amqp.api import testrun_queue_name 

import ots.worker
import ots.worker.tests
from ots.worker.api import worker_factory, SoftTimeoutException
from ots.worker.worker import create_amqp_log_handler

import ots.server.distributor
from ots.server.distributor.taskrunner_factory import taskrunner_factory
from ots.server.distributor.queue_exists import queue_exists
from ots.server.distributor.dev_utils.delete_queues import delete_queue

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

def start_worker(config_filename, amqp_logging = False):
    """
    Start the OTS Worker
    Helper for multiprocessing purposes
    """
    #Make sure ots_mock is on the PATH
    dirname = os.path.dirname(os.path.abspath(ots.worker.__file__))
    os.path.join(dirname, "tests")
    mock_dir = os.path.join(dirname, "tests")
    new_path =  os.environ["PATH"] + ":" + mock_dir
    os.environ["PATH"] = new_path
    #create and start it
    worker = worker_factory(config_filename)
    if amqp_logging:
        amqp_log_handler = create_amqp_log_handler() 
        worker.amqp_log_handler = amqp_log_handler 
    worker.start()

################################################

TEST_DEFINITION_XML = "test_definition.xml"
TEST_DEFINITION_ZIP = "test_definition.zip"

MODULE_DIRNAME = os.path.dirname(os.path.abspath(__file__))
TESTS_MODULE_DIRNAME = os.path.split(MODULE_DIRNAME)[0]



class TestOTSCore(unittest.TestCase):

    def setUp(self):

        config = ConfigParser.ConfigParser()
        config.read(self._worker_config_filename())
        self.queue = config.get('Worker','queue')
        # make sure there is no messages left in the worker queue from previous
        # runs:
        if not DEBUG:
            try:
                delete_queue("localhost", self.queue)
            except:
                pass
        self._worker_processes = []

        self._delete_worker_queue()
        self.testrun_id = None
          
    def tearDown(self):
        for worker_process in self._worker_processes:
            worker_process.terminate()
        time.sleep(2)
        self._remove_zip_file(TEST_DEFINITION_ZIP)
        self._remove_files_created_by_remote_commands()
        if self.queue and not DEBUG:
            delete_queue("localhost", self.queue)
        self._delete_worker_queue()
        if self.testrun_id:
            delete_queue("localhost", testrun_queue_name(self.testrun_id))

    def _delete_worker_queue(self):
        if self.queue and not DEBUG:
            try:
                delete_queue("localhost", self.queue)
            except:
                pass
        

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
        
    def _start_worker_process(self, amqp_logging = False):
        """
        Start a Worker in a separate process
        """
        if not DEBUG:
            worker_config_filename = self._worker_config_filename()
            worker_process = multiprocessing.Process(target = start_worker,
                                    args=(worker_config_filename,),
                                    kwargs={"amqp_logging" :amqp_logging})
            worker_process.start()
            time.sleep(2)
            self._worker_processes.append(worker_process)

    ###################
    # Tests
    ###################


    def test_one_task_one_worker(self):
        """
        Check that the results come back OK from the Worker 
        """
        self._start_worker_process() 
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

        def cb_handler(signal, dto, **kwargs):
            self.cb_called = True
            print 11111111, dto, type(dto)
            filename = dto.results_xml.name 
            if filename == "test_definition.xml":
                self.test_definition_file_received = True
                expected = open(self._dummy_test_definition_xml_fqname(
                                   TEST_DEFINITION_XML), "r").read()
                self.assertEquals(expected, dto.results_xml.read())
            elif filename == "dummy_results_file.xml":
                self.results_file_received = True
                expected = self._dummy_results_xml(filename)
                self.assertEquals(expected, dto.results_xml.read())
            
        DTO_SIGNAL.connect(cb_handler) 
        
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

    def test_amqp_logging(self):
        """
        Check that the results come back OK from the Worker 
        """
        self._start_worker_process(amqp_logging = True) 
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 10,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        command = ["echo", "foo"] 
        taskrunner.add_task(command)

        self.records = []
        def cb_handler(signal, dto, **kwargs):
            if isinstance(dto, LogRecord):
                self.records.append(dto)
          
        DTO_SIGNAL.connect(cb_handler) 
        taskrunner.run()
        messages = ''.join([rec.msg for rec in self.records])
        self.assertTrue("echo foo" in messages)
           
    def test_worker_side_timeout_single_task(self):
        """
        Check that worker timeout works properly.
        It should send error message about the timeout and
        `finish` state change
        """
        self._start_worker_process() 
        self.testrun_id = 111      
        taskrunner = taskrunner_factory(
                             device_group = "foo", 
                             timeout = 1,
                             testrun_id = self.testrun_id,
                             config_file = self._distributor_config_filename())
        command = ["sleep", "10"]

        taskrunner.add_task(command)
        self.cb_called = False
        def cb_handler(signal, sender, dto, **kwargs):
            self.cb_called = True
            self.assertEquals(dto.errno, 6001)
            self.assertTrue(isinstance(dto, SoftTimeoutException))
            self.assertEquals(sender, 'TaskRunner')

        DTO_SIGNAL.connect(cb_handler) 
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
        `finish` state change

        """

        self._start_worker_process() 
        self._start_worker_process() 
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
        def cb_handler(signal, sender, dto, **kwargs):
            self.cb_called += 1
            self.assertEquals(dto.errno, 6001)
            self.assertTrue(isinstance(dto, SoftTimeoutException))
            self.assertEquals(sender, 'TaskRunner')

        DTO_SIGNAL.connect(cb_handler) 
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
        `finish` state change

        """

        self._start_worker_process() 

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
        def cb_handler(signal, sender , dto, **kwargs):
            self.cb_called += 1
            self.assertEquals(dto.errno, 6001)
            self.assertTrue(dto)
            self.assertEquals(sender, 'TaskRunner')

        DTO_SIGNAL.connect(cb_handler) 
        time_before_run = time.time()
        taskrunner.run()
        time_after_run = time.time()
        duration = time_after_run - time_before_run

        self.assertEquals(self.cb_called, 1) # Only one of the commands fails
        self.assertTrue(duration < 6) # Should be less than 10 seconds

    def test_two_tasks_one_worker(self):

        self._start_worker_process()
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
        self._start_worker_process()
        self._start_worker_process()
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
            self.assertTrue(int(time_before_run) <
                            int(foo_time) <= 
                            int(bar_time) <= 
                            int(time_after_run))

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
                              os.path.abspath(ots.server.distributor.__file__))
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
