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

"""Tests for ConductorEngine"""

import sys
import unittest

from ots.server.conductorengine.conductor_command import conductor_command
from ots.server.conductorengine.conductorengine import _get_commands
from ots.server.conductorengine.conductorengine import ConductorEngine

from ots.server.distributor.api import OtsQueueDoesNotExistError, \
    OtsGlobalTimeoutError, OtsQueueTimeoutError, OtsConnectionError

#########################################################################
# Stubs
#########################################################################

class TestRunStub(object):

    def __init__(self):
        self.result_objects = []
        self.state = ""
        self.status_info = ""
        self.error_info = ""
        self.error_code = 0
        self.executed_packages = dict()
        self.result = ""

    def set_result(self, result):
        self.result = result

    def get_timeout(self):
        return 60
    def get_image_url(self):
        return "www.nokia.com"
    def get_testpackages(self): 
        return ["1", "2", "3"]
    def get_host_testpackages(self):
        return ['4','5','6']
    def get_testrun_id(self):
        return 2222
    def get_option(self, arg):
        if arg == "flasher":
            return "asdf/asdfasdf"
        elif arg == "emmc":
            return "asdfasdf"
        elif arg == "device":
            return {"devicegroup":"swproduct1"}
        return '"blah"'

    def add_result_object(self, result):
        self.result_objects.append(result)
    def set_state(self, state, status_info):
        self.state = state
        self.status_info = status_info
    def set_error_info(self, error_info):
        self.error_info = error_info
    def set_error_code(self, error_code):
        self.error_code = error_code

    def add_executed_packages(self, environment, packages):
        """
        add executed packages for one environment
        """
        self.executed_packages[environment] = packages


class TaskrunnerStub(object):
    def __init__(self, exception=None):
        self.tasks = []
        self.executed = False
        self.exception = exception
    def add_task(self, command):
        """
        Add a Task to be run

        @type command: C{list}
        @param command: The CL to be run
        """
        self.tasks.append(command)

    def run(self):
        if self.executed:
            raise Exception("Taskrunner.run() Already called!")
        if self.exception:
            raise self.exception, 4 # Dummy parameter needed by some exceptions
        self.executed = True


#########################################################################
# Tests
#########################################################################

class TestHardwareTestRunner(unittest.TestCase):

    def test_conductor_command_without_testpackages(self):
        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30" }
        expected = ['conductor',  
                    "-u", 'www.nokia.com', '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options,
                                   host_testing = False)
        self.assertEquals(expected, result) 


    def test_conductor_command_with_emmc_flash(self):
        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"Gordon", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30" }
        expected = ['conductor',  
                    '-u', 'www.nokia.com', '-e', 'Gordon', 
                    '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)
        self.assertEquals(expected, result)

    def test_conductor_command_with_flasher_no_pkgs(self):

        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"", 
                   'timeout':"30" }
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_device_pkgs(self):

        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30" }
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)
        self.assertEquals(result, expected)



    def test_device_tests_with_packages(self):
        """Check conductor command with test packages for device"""

        distribution_model = "default"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar,baz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "30"


        expected_cmds = [['conductor', 
                          '-u', 'http://image/url/image.bin', 
                          '-f', '-testsuite=testrunner-tests',
                          '-t', "foo,bar,baz", '-m', '30']]
        
        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout)
        
        self.assertEquals(cmds, expected_cmds)


    def test_custom_distribution_models(self):
        """Check that custom distribution models can be used"""
        self.model_called = 0

        def custom_model1(test_list, options):
            self.model_called = 1
            return ["asdf"]

        distribution_model = "custom1"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar,baz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"
        timeout = "60"


        expected_cmds = ["asdf"]
        
        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout,
                            custom_distribution_models =\
                             [("custom1", custom_model1)])
        
        self.assertEquals(cmds, expected_cmds)


    def test_device_tests_with_no_packages(self):
        """Check conductor command without test packages for device"""

        distribution_model = "default"
        image_url = 'http://image/url/image.bin'
        test_list = {}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "20"


        expected_cmds = [['conductor', 
                          '-u', 'http://image/url/image.bin', 
                          '-f', '-testsuite=testrunner-tests', '-m', '20']]
        
        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout)
        
        self.assertEquals(cmds, expected_cmds)


    def test_host_tests(self):
        """Check conductor command with test packages for host"""


        expected_cmds = [['conductor',
                          '-u', 'http://image/url/image.bin', 
                          '-f', '-testsuite=testrunner-tests',
                          '-t', "foo,bar,baz", '-m', '20',
                          '-o']]


        distribution_model = "default"
        image_url = 'http://image/url/image.bin'
        test_list = {'host':"foo,bar,baz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"
        timeout = "20"

        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout)
        
        self.assertEquals(cmds, expected_cmds)

        

    def test_device_and_host_tests_no_flasher(self):
        """Check conductor command with packages for device and host, without flasherurl."""

        expected_cmds = [['conductor', 
                          '-u', 'http://image/url/image.bin',
                          '-f', '-testsuite=testrunner-tests',
                          '-t', "foo,bar,baz", '-m', '20',
                          ';',
                          'conductor',
                          '-u', 'http://image/url/image.bin', 
                          '-f', '-testsuite=testrunner-tests',
                          '-t', "foo,bar,baz", '-m', '20',
                          '-o']]


        distribution_model = "default"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar,baz",'host':"foo,bar,baz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "20"

        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout)
        
        self.assertEquals(cmds, expected_cmds)

        

    def test_device_and_host_tests_with_flasher(self):
        """Check conductor command with packages for device and host, with flasherurl."""

        expected_cmds = [['conductor', 
                          '-u', 'http://image/url/image.bin',
                          '-f', '-testsuite=testrunner-tests',
                          '--flasherurl', "asdfasdf/asdf",
                          '-t', "foo,bar,baz", '-m', '60',
                          ';',
                          'conductor',
                          '-u', 'http://image/url/image.bin', 
                          '-f', '-testsuite=testrunner-tests',
                          '--flasherurl', "asdfasdf/asdf",
                          '-t', "foo,bar,baz", '-m', '60',
                          '-o']]


        distribution_model = "default"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar,baz",'host':"foo,bar,baz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "60"
        flasher = "asdfasdf/asdf"

        cmds = _get_commands(distribution_model, 
                            image_url, 
                            test_list,
                            emmc_flash_parameter,
                            testrun_id,
                            storage_address,
                            test_filter,
                            timeout,
                            flasher)
        
        self.assertEquals(cmds, expected_cmds)



    def test_device_tests_with_packages_in_distribution_perpackage(self):
        """Test distribution perpackage - device_tests_with_packages"""

        expected_cmd_1 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "foo", '-m', '30']
        expected_cmd_2 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "bar", '-m', '30']

        distribution_model = "perpackage"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "30"

        commands = _get_commands(distribution_model, 
                                image_url, 
                                test_list,
                                emmc_flash_parameter,
                                testrun_id,
                                storage_address,
                                test_filter,
                                timeout)



        self.assertEquals(len(commands), 2)
        self.assertEquals(commands[0], expected_cmd_1)
        self.assertEquals(commands[1], expected_cmd_2)




    def test_device_tests_with_one_pkg_in_distribution_perpackage(self):
        """Test distribution perpackage - device_tests_with_packages"""

        expected_cmd_1 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "foo", '-m', '30']

        distribution_model = "perpackage"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "30"

        commands = _get_commands(distribution_model, 
                                image_url, 
                                test_list,
                                emmc_flash_parameter,
                                testrun_id,
                                storage_address,
                                test_filter,
                                timeout)



        self.assertEquals(len(commands), 1)
        self.assertEquals(commands[0], expected_cmd_1)


    def test_host_tests_with_packages_in_distribution_perpackage(self):
        """Test distribution perpackage - host_tests"""

        expected_cmd_1 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "foo", '-m', '30',
                        '-o']
        expected_cmd_2 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "bar", '-m', '30',
                        '-o']

        distribution_model = "perpackage"
        image_url = 'http://image/url/image.bin'
        test_list = {'host':"foo,bar"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "30"
        commands = _get_commands(distribution_model, 
                                image_url, 
                                test_list,
                                emmc_flash_parameter,
                                testrun_id,
                                storage_address,
                                test_filter,
                                timeout)
        
        self.assertEquals(len(commands), 2)
        self.assertEquals(commands[0], expected_cmd_1)
        self.assertEquals(commands[1], expected_cmd_2)


    def test_device_and_host_tests_in_distribution_perpackage(self):
        """Test distribution perpackage - device_and_host_tests"""

        expected_cmd_1 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "foo", '-m', '10']
        expected_cmd_2 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "bar", '-m', '10']
        expected_cmd_3 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "baz", '-m', '10',
                        '-o']
        expected_cmd_4 = ['conductor', 
                        '-u', 'http://image/url/image.bin', 
                        '-f', '-testsuite=testrunner-tests',
                        '-t', "yaz", '-m', '10',
                        '-o']

        distribution_model = "perpackage"
        image_url = 'http://image/url/image.bin'
        test_list = {'device':"foo,bar",'host':"baz,yaz"}
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = ""
        timeout = "10"
        test_filter = "-testsuite=testrunner-tests"  
        commands = _get_commands(distribution_model, 
                                image_url, 
                                test_list,
                                emmc_flash_parameter,
                                testrun_id,
                                storage_address,
                                test_filter,
                                timeout)

        self.assertEquals(len(commands), 4)
        self.assertEquals(commands[0], expected_cmd_1)
        self.assertEquals(commands[1], expected_cmd_2)
        self.assertEquals(commands[2], expected_cmd_3)
        self.assertEquals(commands[3], expected_cmd_4)


    def test_device_tests_with_no_packages_in_distribution_perpackage(self):
        """Test distribution perpackage - no packages"""

        distribution_model = "perpackage"
        image_url = 'http://image/url/image.bin'
        test_list = {} #no packages
        emmc_flash_parameter = "" 
        testrun_id = "" 
        storage_address = "" 
        test_filter = "-testsuite=testrunner-tests"  
        timeout = "30"
        self.assertRaises(ValueError,
                          _get_commands,
                          distribution_model, 
                          image_url, 
                          test_list,
                          emmc_flash_parameter,
                          testrun_id,
                          storage_address,
                          test_filter,
                          timeout)



#######################################################################

class TestConductorEngine(unittest.TestCase):

    def test_init_hardware_test(self):
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        ots_ta_adapter = ConductorEngine(ots_config)
        
        test_run = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(test_run)
        
        self.assertEquals("swproduct1", 
                          ots_ta_adapter._routing_key)
        self.assertEquals(3600, 
                          ots_ta_adapter._timeout)
        self.assertEquals("www.nokia.com",
                          ots_ta_adapter._image_url)
        self.assertEquals({'device':"1,2,3", 'host':'4,5,6'},
                          ots_ta_adapter._test_list)
        self.assertEquals("asdfasdf",
                          ots_ta_adapter._emmc_flash_parameter)
        self.assertEquals(2222,
                          ots_ta_adapter._testrun_id)
        self.assertEquals("host:port", 
                          ots_ta_adapter._storage_address)

        self.assertEquals('"\'blah\'"',
                          ots_ta_adapter._test_filter)

        self.assertEquals("asdf/asdfasdf",
                          ots_ta_adapter._flasher)


    def test_execute(self):
        
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub()
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        expected_tasks = [['conductor',
                          '-u', 'www.nokia.com',
                          '-e', 'asdfasdf',
                          '-i', '2222',
                          '-c', 'host:port',
                          '-f', '"\'blah\'"',
                          '--flasherurl', 'asdf/asdfasdf',
                          '-t', '1,2,3', '-m', '3600',
                          ';',
                          'conductor',
                          '-u', 'www.nokia.com',
                          '-e', 'asdfasdf',
                          '-i', '2222',
                          '-c', 'host:port',
                          '-f', '"\'blah\'"',
                          '--flasherurl', 'asdf/asdfasdf',
                          '-t', '4,5,6', '-m', '3600',
                          '-o']]
        self.assertEquals(taskrunner.tasks, expected_tasks)
        self.assertEquals(taskrunner.executed, True)


    def test_handle_generic_exception(self):
        
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub(Exception())
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        self.assertEquals(testrun.error_info,
                          'A miscellaneous error was encountered')
        self.assertEquals(testrun.result, "ERROR")


    def test_handle_queue_does_not_exist_exception(self):
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub(OtsQueueDoesNotExistError)
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        self.assertEquals(testrun.error_info,
                          "Queue '%s' does not exist" % \
                              ots_ta_adapter._routing_key)

        self.assertEquals(testrun.result, "ERROR")



    def test_handle_global_timeout_exception(self):
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub(OtsGlobalTimeoutError)
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        expected = "Server side timeout. (Worker went offline during testrun or some tasks were not started in time)"
        self.assertEquals(testrun.error_info, expected)


        self.assertEquals(testrun.result, "ERROR")


    def test_handle_worker_start_timeout_exception(self):
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub(OtsQueueTimeoutError)
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        expected =\
            "The job was not started within 0 minutes. A worker in that devicegroup may be down or there may be exceptional demand"

        self.assertEquals(testrun.error_info, expected)
        self.assertEquals(testrun.result, "ERROR")

    def test_handle_connection_exception(self):
        ots_config = {}
        ots_config['host'] = "host"
        ots_config['port'] = "port"

        taskrunner = TaskrunnerStub(OtsConnectionError)
        ots_ta_adapter = ConductorEngine(ots_config, taskrunner)
        
        testrun = TestRunStub()
        ots_ta_adapter._init_ots_from_testrun(testrun)
        ots_ta_adapter.execute(testrun)
        expected = 'A connectivity issue was encountered'

        self.assertEquals(testrun.error_info, expected)
        self.assertEquals(testrun.result, "ERROR")






if __name__ == "__main__":
    unittest.main()
