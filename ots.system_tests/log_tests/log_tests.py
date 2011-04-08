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
OTS log based system tests.

These tests expect that you have full ots system set up. They trigger testruns
and check http logs for expected results

Make sure there is no other activities going on in the system while running 
the tests!

Please check that system_tests.conf is up to date!

"""

import unittest
import os
import configobj
from configobj import ConfigObj

from ots.tools.trigger.ots_trigger import ots_trigger
from log_scraper import has_message, has_errors
from log_scraper import get_latest_testrun_id, get_second_latest_testrun_id


############################################
# CONFIG
############################################

CONFIGFILE = "log_tests.conf"
CONFIG = ConfigObj(CONFIGFILE).get("log_tests")

############################################
# DEFAULT OPTIONS
############################################

class Options(object):
    """
    A mock for ots_trigger options
    """

    def __init__(self):
        self.id = 0
        self.sw_product = CONFIG["sw_product"]
        self.image = CONFIG["image_url"]
        self.testpackages = ""
        self.hosttest = ""
        self.deviceplan = ""
        self.hostplan = ""
        self.rootstrap = ""
        self.chroottest = ""
        self.distribution = "default"
        self.filter = ""
        self.input_plugin = ""
        self.device = CONFIG["device"]
        self.email = CONFIG["email"]
        self.timeout = 30
        self.server = CONFIG["server"]

############################################
#  BASE
############################################

class SystemSingleRunTestCaseBase(unittest.TestCase):
    """
    Base class for a single run 
    where log of the last testrun are scraped
    and compared against the expected strings

    Helpers add descriptive error formatting
    """
    @staticmethod
    def _print_options(options):
        print "************************"
        print "Triggering Testrun with Options:"
        print "SW Product: %s"%(options.sw_product)
        print "Image: %s"%(options.image)
        print "Hosttest: %s"%(options.hosttest)
        print "Testpackages: %s"%(options.testpackages)
        print "Device: %s" %(options.device)
        if options.filter:
            print "Filters: %s" % options.filter

    @property
    def testrun_id(self):
        return get_latest_testrun_id(CONFIG["global_log"])

    def _has_errors(self):
        return has_errors(CONFIG["global_log"], self.testrun_id)

    def _has_message(self, string):
        return has_message(CONFIG["global_log"],
                           self.testrun_id, 
                           string)

    def _replace_keywords(self, strings):
        new_string = []
        for string in strings:
            new_string.append(string.replace("__TESTRUN_ID__", self.testrun_id))
        return new_string

    def assert_log_contains_string(self, string): 
        self.assertTrue(self._has_message(string), 
                        "'%s' not found on log for testrun_id: '%s'" \
                        % (string, self.testrun_id))

    def assert_log_doesnt_contain_string(self, string):
        self.assertFalse(self._has_message(string), 
                        "'%s' not found on log for testrun_id: '%s'" \
                        % (string, self.testrun_id))

    def assert_log_contains_strings(self, strings):
        for string in strings:
            self.assert_log_contains_string(string)

    def assert_log_doesnt_contain_strings(self, strings):
        for string in strings:
            self.assert_log_doesnt_contain_string(string)

    def assert_true_log_has_errors(self):
        self.assertTrue(self._has_errors(),
                        "Error messages no found for testrun_id: '%s'" \
                        % (self.testrun_id))

    def assert_false_log_has_errors(self):
        self.assertFalse(self._has_errors(),
                        "Error messages no found for testrun_id: '%s'" \
                        % (self.testrun_id))

    def assert_result_is_pass(self, result):
        self.assert_log_contains_string("Testrun finished with result: PASS")
        self.assertEquals(result, 
                          "PASS",
                          "Assertion error: result fails testrun_id: '%s'"\
                         % (self.testrun_id))
        
    def assert_result_is_error(self, result):
        self.assert_log_contains_string("Result set to ERROR")
        self.assertEquals(result, 
                          "ERROR",
                          "Assertion error: result fails testrun_id: '%s'"\
                         % (self.testrun_id))

    def trigger_testrun_expect_pass(self, options, strings):
        self._print_options(options)
        result = ots_trigger(options)
        self.assert_result_is_pass(result)
        self.assert_false_log_has_errors()
        self.assert_log_contains_strings(self._replace_keywords(strings))

    def trigger_testrun_expect_error(self, options, strings):
        self._print_options(options)
        result = ots_trigger(options)
        self.assert_result_is_error(result)
        self.assert_true_log_has_errors()
        self.assert_log_contains_strings(self._replace_keywords(strings))

############################################
# TestHWBasedSuccessfulTestruns
############################################

class TestHWBasedSuccessfulTestruns(SystemSingleRunTestCaseBase):

    def test_hw_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.testpackages = "test-definition-tests"
        options.timeout = 30
        expected = ["Environment: Hardware",
                    "Starting conductor at",
                    """Finished running tests."""]
        self.trigger_testrun_expect_pass(options, expected)

    def test_hw_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        expected = ["Starting conductor at",
          "Finished running tests.",
          "Testrun ID: __TESTRUN_ID__  Environment: Hardware",
          "Beginning to execute test package: test-definition-tests",
          "Beginning to execute test package: testrunner-lite-regression-test",
          "Executed 1 cases. Passed 1 Failed 0"]
        self.trigger_testrun_expect_pass(options, expected)

    def test_hw_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution = "default"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Testrun finished with result: PASS",
                    "Starting conductor at",
                    "Finished running tests.",
                    "Environment: Hardware"]
        self.trigger_testrun_expect_pass(options, expected)
    
    def test_hw_based_testrun_with_testplan(self):
        options = Options()
        options.distribution = "default"
        options.deviceplan = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Testrun finished with result: PASS",
                    "Starting conductor at",
                    "Finished running tests.",
                    "Environment: Hardware",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0"]
        self.trigger_testrun_expect_pass(options, expected)
    
    def test_hw_based_testrun_with_multiple_testplan(self):
        options = Options()
        options.distribution = "default"
        options.deviceplan = ["data/echo_system_tests.xml",
                              "data/ls_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Testrun finished with result: PASS",
                    "Starting conductor at",
                    "Finished running tests.",
                    "Environment: Hardware",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0",
                    "Beginning to execute test package: ls_system_tests.xml"]
        self.trigger_testrun_expect_pass(options, expected)

############################################
# TestHostBasedSuccessfulTestruns
############################################

class TestHostBasedSuccessfulTestruns(SystemSingleRunTestCaseBase):

    def test_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.testpackages = ""
        options.timeout = 30
        expected = ["Testrun finished with result: PASS",
                    "Environment: Host_Hardware",
                    "Starting conductor at",
                    """Finished running tests."""]
        self.trigger_testrun_expect_pass(options, expected)
        self.assert_log_doesnt_contain_string("Environment: Hardware")

    def test_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        expected = ["Starting conductor at",
          "Finished running tests.",
          "Testrun ID: __TESTRUN_ID__  Environment: Host_Hardware",
          "Beginning to execute test package: test-definition-tests",
          "Beginning to execute test package: testrunner-lite-regression-test",
          "Executed 1 cases. Passed 1 Failed 0"]
        self.trigger_testrun_expect_pass(options, expected)

    def test_host_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution = "default"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_host_based_testrun_with_testplan(self):
        options = Options()
        options.distribution = "default"
        options.hostplan = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0"]
        self.trigger_testrun_expect_pass(options, expected)
    
    def test_host_based_testrun_with_multiple_testplan(self):
        options = Options()
        options.distribution = "default"
        options.hostplan = ["data/echo_system_tests.xml",
                              "data/ls_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0",
                    "Beginning to execute test package: ls_system_tests.xml"]
        self.trigger_testrun_expect_pass(options, expected)

############################################
# TestChrootBasedSuccessfulTestruns
############################################

class TestChrootBasedSuccessfulTestruns(SystemSingleRunTestCaseBase):

    def test_chroot_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.timeout = 30
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = "test-definition-tests"
        expected = ["Environment: chroot",
                    "Starting conductor at",
                    "Finished running tests.",
                    "Testrun finished with result: PASS",
                    "Testing in chroot done. No errors."]
        self.trigger_testrun_expect_pass(options, expected)

    def test_chroot_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = \
            "test-definition-tests testrunner-lite-regression-tests"

        expected = ["Starting conductor at",
          "Finished running tests.",
          "Testrun ID: __TESTRUN_ID__  Environment: chroot",
          "Beginning to execute test package: test-definition-tests",
          "Beginning to execute test package: testrunner-lite-regression-test",
          "Executed 1 cases. Passed 1 Failed 0",
          "Testing in chroot done. No errors."]
        self.trigger_testrun_expect_pass(options, expected)

    def test_chroot_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution = "default"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = \
            "test-definition-tests testrunner-lite-regression-tests"
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: chroot",
                    "Testing in chroot done. No errors."]
        self.trigger_testrun_expect_pass(options, expected)

############################################
# TestMixedSuccessfulTestruns
############################################

class TestMixedSuccessfulTestruns(SystemSingleRunTestCaseBase):

    def test_hw_and_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.testpackages = "test-definition-tests"
        options.timeout = 60
        expected = ["Environment: Hardware",
                    "Environment: Host_Hardware",
                    "Starting conductor at",
                    """Finished running tests."""]
        self.trigger_testrun_expect_pass(options, expected)

    def test_hw_and_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 120
        expected = ["Starting conductor at",
          "Environment: Host_Hardware",
          "Environment: Hardware",
          "Finished running tests."]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_hw_and_host_based_testplans(self):
        options = Options()
        options.distribution = "default"
        options.deviceplan = ["data/ls_system_tests.xml"]
        options.hostplan = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware",
                    "Environment: Hardware",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0",
                    "Beginning to execute test package: ls_system_tests.xml"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_hw_test_package_and_test_plan(self):
        options = Options()
        options.distribution = "default"
        options.deviceplan = ["data/ls_system_tests.xml"]
        options.testpackages = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Hardware",
                    "Beginning to execute test package: ls_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0",
                    "Beginning to execute test package: test-definition-tests"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_host_test_package_and_test_plan(self):
        options = Options()
        options.distribution = "default"
        options.hostplan = ["data/ls_system_tests.xml"]
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware",
                    "Beginning to execute test package: ls_system_tests.xml",
                    "Executed 1 cases. Passed 1 Failed 0",
                    "Beginning to execute test package: test-definition-tests"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_host_and_hw_test_package_and_test_plan(self):
        options = Options()
        options.distribution = "default"
        options.deviceplan = ["data/echo_system_tests.xml"]
        options.testpackages = "test-definition-tests"
        options.hostplan = ["data/ls_system_tests.xml"]
        options.hosttest = "testrunner-lite-regression-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Starting conductor at",
                    "Finished running tests.",
                    "Environment: Host_Hardware",
                    "Environment: Hardware",
                    "Beginning to execute test package: ls_system_tests.xml",
                    "Beginning to execute test package: echo_system_tests.xml",
                    "Beginning to execute test package: test-definition-tests",
                    "Beginning to execute test package: testrunner-lite-regression-tests"]
        self.trigger_testrun_expect_pass(options, expected)


    def test_hw_host_chroot_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.testpackages = "test-definition-tests"
        options.chroottest = "test-definition-tests"
        options.rootstrap = CONFIG["rootstrap_url"]
        options.timeout = 60
        expected = ["Environment: Hardware",
                    "Environment: Host_Hardware",
                    "Environment: chroot",
                    "Starting conductor at",
                    """Finished running tests."""]
        self.trigger_testrun_expect_pass(options, expected)

############################################
# TestMiscSuccessfulTestruns
############################################

class TestMiscSuccessfulTestruns(SystemSingleRunTestCaseBase):

    def test_testrun_with_filter(self):
        options = Options()
        options.testpackages = "testrunner-lite-regression-tests"
        options.timeout = 30
        options.filter = "testcase=trlitereg01,trlitereg02"
        #
        self._print_options(options)
        result = ots_trigger(options)
        self.assert_result_is_pass(result)
        self.assert_false_log_has_errors()
        self.assert_log_contains_string("Testrun finished with result: PASS")
        expected = ["Test case quoting_01 is filtered",
                    "Test case quoting_01 is filtered",
                    "Executed 2 cases. Passed 2 Failed 0"]
        self.assert_log_contains_strings(expected)
        expected = ["Test case trlitereg01 is filtered",
                    "Test case trlitereg02 is filtered"]
        self.assert_log_doesnt_contain_strings(expected)


############################################
# TestCustomDistributionModels
############################################

class TestCustomDistributionModels(SystemSingleRunTestCaseBase):

    def test_load_example_distribution_model(self):
        """
        test_load_example_distribution_model

        To make this case pass example distribution model needs to be
        installed. It can be found from examples directory.
        """
        options = Options()
        options.distribution = "example_model"
        options.timeout = 1
        self.trigger_testrun_expect_error(options, 
                        ["Example distribution model not implemented"])

    def test_load_invalid_distribution_model(self):
        options = Options()
        options.distribution = "invalid_distribution_model"
        options.timeout = 1
        self.trigger_testrun_expect_error(options,
                        ["ValueError: Invalid distribution model"])
        
    def test_load_optimized_distribution_model_for_host_packages(self):
        options = Options()
        options.hosttest = "test-definition-tests testrunner-lite-regression-tests"
        options.distribution = "optimized"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Beginning to execute test package: test-definition-tests",
                    "Beginning to execute test package: testrunner-lite-regression-tests",
                    "Loaded custom distribution model 'ots.plugin.history.distribution_model'",
                    "Environment: Host_Hardware",
                    ]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_load_optimized_distribution_model_for_hw_packages(self):
        options = Options()
        options.testpackages = "test-definition-tests testrunner-lite-regression-tests"
        options.distribution = "optimized"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        expected = ["Beginning to execute test package: test-definition-tests",
                    "Beginning to execute test package: testrunner-lite-regression-tests",
                    "Loaded custom distribution model 'ots.plugin.history.distribution_model'",
                    "Environment: Hardware",
                    ]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_optimized_without_packages(self):
        options = Options()
        options.distribution = "optimized"
        options.deviceplan = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 10
        
        self.trigger_testrun_expect_error(options, 
                    ["No commands created"])


##########################################
# TestErrorConditions
##########################################

class TestErrorConditions(SystemSingleRunTestCaseBase):

    def test_bad_image_url(self):
        options = Options()
        options.image = options.image+"asdfasdfthiswontexistasdfasdf"
        options.testpackages = "testrunner-lite-regression-tests"
        options.timeout = 30
        path = os.path.basename(options.image)
        expected = ["Error: Could not download file %s, Error code: 103" % path,
                    "Starting conductor at"]
        self.trigger_testrun_expect_error(options, expected)
    
    def test_timeout(self):
        options = Options()
        options.testpackages = "testrunner-lite-regression-tests"
        options.timeout = 1
        expected = ["Error: Timeout while executing test package " \
                    "testrunner-lite-regression-tests, Error code: 1091",
                    "Test execution error: Timeout while executing test " \
                    "package testrunner-lite-regression-tests"]
        self.trigger_testrun_expect_error(options, expected)

    def test_non_existing_devicegroup(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist"
        options.timeout = 1
        expected = [
          "No queue for this_should_not_exist",
          "Incoming request: program: ots-system-tests, request: 0, " \
          "notify_list: ['%s'], options: {"  % (CONFIG["email"]),
          "'image': '%s'" % (CONFIG["image_url"]),
          "'distribution_model': 'default'",
          "'timeout': 1",
          "'device': 'devicegroup:this_should_not_exist'"]
        self.trigger_testrun_expect_error(options, expected)

    def test_non_existing_sw_product(self):
        options = Options()
        options.sw_product = "this_should_not_exist"
        options.timeout = 1
        expected = [
           "'this_should_not_exist' not found",
           "Incoming request: program: this_should_not_exist, request: 0, " \
           "notify_list: ['%s'], options: {"  % (CONFIG["email"]),
           "'image': '%s'" % (CONFIG["image_url"]),
           "'distribution_model': 'default'",
           "'timeout': 1"]
        self.trigger_testrun_expect_error(options, expected)

    def test_bad_testpackage_names(self):
        options = Options()
        options.testpackages = "test-definition-tests thisisnotatestpackage"
        options.timeout = 1
        self.trigger_testrun_expect_error(options, 
                            ["Invalid testpackage(s): thisisnotatestpackage"])

    def test_no_image_url(self):
        options = Options()
        options.timeout = 1
        options.image = ""
        self.trigger_testrun_expect_error(options, 
                            ["Missing `image` parameter"])

    def test_bad_distribution_model(self):
        options = Options()
        options.distribution = "sendalltestrunstowastebin"
        options.timeout = 1
        self.trigger_testrun_expect_error(options,
                      ["Invalid distribution model: sendalltestrunstowastebin"])

    def test_perpackage_distribution_no_packages(self):
        options = Options()
        options.distribution = "perpackage"
        options.timeout = 1
        
        self.trigger_testrun_expect_error(options, 
                    ["Test packages must be defined for specified " \
                     "distribution model 'perpackage'"])

########################################
# TestDeviceProperties
########################################

class TestDeviceProperties(unittest.TestCase):

    def test_multiple_devicegroups(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist_1;devicegroup:" \
            "this_should_not_exist_either"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with multiple devicegroups: '%s'"\
            % options.device
        print "Please make sure the system does not have these devicegroups."
        print "Checking that a separate testrun gets created for all " \
            "devicegroups."

        old_testrun = get_latest_testrun_id(CONFIG["global_log"])
        print "latest testrun_id before test: %s" % old_testrun
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id(CONFIG["global_log"])
        testrun_id2 = get_latest_testrun_id(CONFIG["global_log"])
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2

        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(CONFIG["global_log"],
                                   testrun_id1))
        self.assertTrue(has_errors(CONFIG["global_log"],
                                   testrun_id2))

        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)
        string1 = """No queue for this_should_not_exist_1"""
        string2 = """No queue for this_should_not_exist_either"""
        
        if (has_message(CONFIG["global_log"], 
                        testrun_id1, 
                        string1)):
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string2))
        else:
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string1))
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id1, 
                                        string2))

    def test_one_devicegroup_multiple_devicenames(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:" \
            "device1;devicegroup:this_should_not_exist devicename:device2"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with one devicegroup, multiple " \
            "devicenames: '%s'" % options.device
        print "Please make sure the system does not have the devicegroup."
        print "Checking that a separate testrun gets created for all " \
            "devicenames."
        
        old_testrun = get_latest_testrun_id(CONFIG["global_log"])
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id(CONFIG["global_log"])
        testrun_id2 = get_latest_testrun_id(CONFIG["global_log"])

        print "latest testrun_id before test: %s" % old_testrun
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2

        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(CONFIG["global_log"], testrun_id1))
        self.assertTrue(has_errors(CONFIG["global_log"], testrun_id2))

        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)

        string1 = """No queue for this_should_not_exist.device1"""
        string2 = """No queue for this_should_not_exist.device2"""
        
        if (has_message(CONFIG["global_log"], testrun_id1, string1)):
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string2))
        else:
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string1))
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id1, 
                                        string2))


    def test_one_devicegroup_one_devicename_multiple_device_ids(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:" \
            "device1 deviceid:id1;devicegroup:this_should_not_exist " \
            "devicename:device1 deviceid:id2"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with one devicegroup, one devicename, " \
            "multiple device ids: '%s'" % options.device
        print "Please make sure the system does not have the devicegroup."
        print "Checking that a separate testrun gets created for all " \
            "devicenames."
        
        old_testrun = get_latest_testrun_id(CONFIG["global_log"])
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id(CONFIG["global_log"])
        testrun_id2 = get_latest_testrun_id(CONFIG["global_log"])

        print "latest testrun_id before test: %s" % old_testrun
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2


        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(CONFIG["global_log"], testrun_id1))
        self.assertTrue(has_errors(CONFIG["global_log"], testrun_id2))
        

        # Make sure correct routing keys are used
        string1 = """No queue for this_should_not_exist.device1.id1"""
        string2 = """No queue for this_should_not_exist.device1.id2"""
        
        if (has_message(CONFIG["global_log"],
                        testrun_id1, 
                        string1)):
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string2))
        else:
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id2, 
                                        string1))
            self.assertTrue(has_message(CONFIG["global_log"],
                                        testrun_id1, 
                                        string2))

########################################
# TestPlugins
########################################

class TestPlugins(SystemSingleRunTestCaseBase):

    def test_plugins_loaded(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.filter = "testcase=Check-basic-schema"
        expected = ["Monitor Plugin loaded",
                    "history data saved",
                    "Using smtp server",
                    "Email sent"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_email_invalid_address(self):
        options = Options()
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.image = ""
        options.email = "invalid_email_address"
        expected = ["Missing `image` parameter"]
        self.trigger_testrun_expect_error(options, expected)
    

class TestMultiDevice(SystemSingleRunTestCaseBase):
    
    #
    # These tests are requiring that one ots-worker
    # is started as number 1 and uses meego-ai-flasher-n900
    # flasher.
    #
    
    def test_load_flasher_plugin(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.filter = "testcase=Check-basic-schema"
        expected = ["Loaded flasher 'meego-ai-flasher-n900'"]
        self.trigger_testrun_expect_pass(options, expected)
        
    def test_load_separated_settings(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.filter = "testcase=Check-basic-schema"
        expected = ["using config file /etc/conductor_1.conf"]
        self.trigger_testrun_expect_pass(options, expected)

if __name__ == "__main__":
    unittest.main()
